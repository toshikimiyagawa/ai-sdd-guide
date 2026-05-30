# Design: Multi-Agent Orchestration for SDD

**Date:** 2026-05-30  
**Status:** Approved

## 概要

Claude が設計を担い、Codex / Gemini 等が実装を担うマルチエージェントフローを
`ai-sdd-guide` の `orchestration/` モジュールとして実装する。
フェーズレベルとタスクレベルの両粒度でスコープ分割し、
ファイル規約・hooks・CI・ハンドオフ成果物による多層Enforcementで守る。

## アーキテクチャ

既存の `ai-sdd-guide` に `orchestration/` ディレクトリを追加する。

```
ai-sdd-guide/
├── rules/              # 既存
├── templates/          # 既存
├── integration/        # 既存
├── docs/               # 既存
└── orchestration/      # 新規（オプション機能）
    ├── rules/
    │   └── orchestration.md              # agent向けスコープ・引き継ぎルール
    ├── schema/
    │   ├── agent-assignment.schema.json  # スコープ→agent割り当て定義
    │   └── tasks.schema.json             # tasks.json のスキーマ
    ├── templates/
    │   ├── agent-assignment.example.json # .sdd/ に置く設定例
    │   └── handoff.md.example            # ハンドオフ成果物の雛形
    ├── tools/
    │   └── kanban.sh                     # tasks.json をKanban表示するCLI
    └── integration/
        ├── settings-patch.json           # enforcement hooks 追加分
        └── AGENTS-patch.md.example       # 非Claude agent向けCLAUDE/AGENTS.md追加分
```

取り込み側プロジェクトでは以下の2ファイルが `.sdd/` に追加される：

```
.sdd/
  state.json             # 既存：現在作業中フィーチャーのフェーズ/Tier（1件）
  agent-assignment.json  # 新規：タスクパターン→agent割り当てルール
  tasks.json             # 新規：プロジェクト全タスクの状態一覧（Kanbanのデータソース）
```

> `state.json` は「今 hooks/CI が参照する現在状態」、`tasks.json` は「人間が俯瞰するための全体状態」という役割分担。

取り込み側での有効化は `CLAUDE.md` への1行追加のみ：

```
@vendor/ai-sdd-guide/orchestration/rules/orchestration.md
```

## コアコンセプト

### フェーズレベルのスコープ（固定）

| フェーズ | 担当可能Agent | 備考 |
|---|---|---|
| brainstorm / spec / plan | Claude のみ | superpowers必須 |
| implement | Claude / Codex / Gemini | タスク単位で割り当て可 |
| verify / review | Claude のみ | sdd-reviewer subagent |

### タスクレベルの割り当て（`agent-assignment.json`）

取り込み側が `.sdd/agent-assignment.json` を置いて宣言する：

```json
{
  "default_implementer": "codex",
  "rules": [
    { "pattern": "feat/frontend-*", "agent": "gemini" },
    { "pattern": "feat/api-*",      "agent": "codex"  },
    { "pattern": "feat/infra-*",    "agent": "claude" }
  ]
}
```

### `tasks.json` のデータ構造

```json
[
  {
    "id": "feat-login",
    "phase": "implement",
    "assigned_agent": "codex",
    "status": "in_progress",
    "handoff": "specs/feat-login/handoff.md",
    "blocked_reason": null
  },
  {
    "id": "feat-payment",
    "phase": "spec",
    "assigned_agent": "claude",
    "status": "pending",
    "handoff": null,
    "blocked_reason": null
  }
]
```

ステータス遷移：

```
pending → in_progress → completed
                      → blocked   (曖昧・仕様不備 → Claudeにエスカレーション)
```

## ハンドオフプロトコル

スコープ間の引き継ぎは**成果物ベース**で行う。Agentが次のAgentに口頭指示するのではなく、ファイルが契約になる。

```
Claude (設計)                    Codex/Gemini (実装)
────────────────                 ───────────────────
brainstorm → spec → plan
         ↓
  handoff.md を生成
  tasks.json を更新 (pending → in_progress)
         ↓ ─────────────────────→ handoff.md を読む
                                   実装する
                                   tasks.json を更新 (in_progress → completed)
                                         ↓
                              ←───────── 完了を宣言
Claude (検証)
sdd-reviewer が実行
```

### `handoff.md` の構造（雛形）

```markdown
# Handoff: <feature-id>

## あなたのスコープ
実装フェーズのみ。spec / plan / verify には触れない。

## 完了条件
- [ ] specs/<feature>/tasks.md の全タスクが完了
- [ ] テストがパス

## 参照ファイル
- spec:  specs/<feature>/spec.md
- plan:  specs/<feature>/plan.md
- tasks: specs/<feature>/tasks.md

## 曖昧な点があれば
実装を止めて tasks.json の status を "blocked" にし、
blocked_reason に理由を記載してエスカレーション。
```

## Enforcement（多層防御）

| Layer | タイミング | バイパス可否 | 担当 |
|---|---|---|---|
| ファイル規約（CLAUDE.md/AGENTS.md） | 即時 | 可 | 全Agent |
| Claude hooks（sdd-orchestration-guard.sh） | 即時 | 可 | Claude |
| CI（sdd-check.yml 追加チェック） | PR時 | 不可 | 全Agent |
| ハンドオフ成果物（handoff.md 必須） | PR時 | 不可 | 全Agent |

### Layer 1: ファイル規約
- `CLAUDE.md` に `orchestration/rules/orchestration.md` を追記 → Claude がスコープ外を自覚
- `AGENTS.md` に非Claude Agent向けスコープ制限を追記

### Layer 2: Claude hooks（`sdd-orchestration-guard.sh`）
- `state.json` の `phase` が `implement` かつ `assigned_agent` が `claude` 以外のとき
  Claude がソース編集しようとしたら警告・ブロック

### Layer 3: CI（`sdd-check.yml` への追加）
- `implement` フェーズ開始前に `handoff.md` の存在チェック
- `tasks.json` に `status: "blocked"` が残っていたら失敗
- verify フェーズ移行前に全タスク `completed` チェック

### Layer 4: ハンドオフ成果物
- `handoff.md` なしで実装フェーズに進めない（CI で弾く）
- `blocked` 状態は Claudeがエスカレーション解決するまで前進不可

## 可視化（Kanban）

`orchestration/tools/kanban.sh` が `.sdd/tasks.json` を読んでテキスト形式で表示：

```
PENDING          IN_PROGRESS      COMPLETED        BLOCKED
─────────────    ─────────────    ─────────────    ─────────────
feat-payment     feat-login       feat-auth
[claude/spec]    [codex/impl]     [claude/verify]
```

将来的に GitHub Projects / Web UI への連携もこの JSON をデータソースとして使える。

## 導入手順（取り込み側）

```bash
# 1. CLAUDE.md に1行追加
echo "@vendor/ai-sdd-guide/orchestration/rules/orchestration.md" >> CLAUDE.md

# 2. agent-assignment.json を配置
cp vendor/ai-sdd-guide/orchestration/templates/agent-assignment.example.json .sdd/agent-assignment.json
# → プロジェクトに合わせて編集

# 3. hooks を追加
# settings-patch.json の内容を .claude/settings.json にマージ

# 4. CI を更新
# sdd-check.yml に orchestration チェックを追加
```

## 未解決事項

なし。

## スコープ外

- Web UI / ダッシュボードの実装（JSON提供のみ）
- 特定CIプロバイダー以外のCI連携
- Agent間のリアルタイム通信
