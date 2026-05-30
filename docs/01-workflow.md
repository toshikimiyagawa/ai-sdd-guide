# 01. ワークフロー

## Tier制（規模に応じて省略可）
全タスクは最初に Tier を判定する。迷ったら上位を選ぶ。

| Tier | 対象 | 作るもの |
|---|---|---|
| 0 | typo・コメント・docのみ・整形 | 何も作らず実施 |
| 1 | 局所的なbugfix・小さな変更 | 軽量spec（意図＋受入条件）＋テスト。plan/tasks は省略 |
| 2 | 新機能・複数ファイル・設計変更・公開API | spec → plan → tasks → 実装 → 検証 をフル |

判定結果は `.sdd/state.json` に記録し、PRラベル `sdd:tier-N` を付ける（hooks/CI が参照）。

## フェーズ

### 設計（superpowers必須）
1. **brainstorm** — 人間と意図をすり合わせる（superpowers）。
2. **spec** — `specs/<feature>/spec.md`。受入条件を「チェック可能な文」で書き、人間承認を得る。
3. **plan** — `plan.md`。アプローチ・影響ファイル・トレードオフ・代替案。(Tier 2)
4. **tasks** — `tasks.md`。順序付きの具体タスク＋各受入条件に対応するテスト。(Tier 2)
5. **freeze** — `.sdd/state.json` を `phase=implement` に。ここが他agentへの引き渡しゲート。

### 実装（任意のagent）
- `specs/<feature>/` を読み、凍結された tasks を**そのまま**実装する（過不足なく）。
- 受入条件は必ずテストに対応させる。
- spec が間違っていたら**止めて人間にエスカレーション**。勝手に再設計しない。

### 検証（superpowers必須）
- テスト実行。`sdd-reviewer` subagent で凍結specへの適合を独立監査。
- PR を作成し、CI が全てパスしてマージ可能な状態であることを確認してから完了とする。
- 最終的な合否は CI が独立に再判定する。

## 省略の基準
- Tier 0：spec不要（hooks/CIも免除）。
- Tier 1：軽量spec必須、plan/tasks省略可。
- Tier 2：省略しない。

「小さいから省く」判断は `.sdd/state.json` と PRラベルで宣言し、後から検証できる形にする。
これにより hooks（ローカル）と CI（権威）が機械的に Tier を判定できる。

## 状態ファイル `.sdd/state.json`
現在の作業の Tier とフェーズを記録する。作業中に agent が作成・更新し、hooks と CI がこれを読んで逸脱を判定する。

| フィールド | 必須 | 値 | 説明 |
|---|---|---|---|
| `tier` | ○ | 0 / 1 / 2 | タスクの規模 |
| `phase` | ○ | brainstorm / spec / plan / tasks / implement / verify / done | 現在フェーズ。hookは implement/verify（またはTier 0）でのみソース編集を許可 |
| `feature` | - | slug | `specs/<feature>/` に対応 |
| `spec` | - | path | 有効な spec ディレクトリのパス |
| `note` | - | text | Tier 0/1 免除の理由（監査用） |

雛形: `templates/sdd-state.example.json` ／ 値の定義: `templates/sdd-state.schema.json`（JSON Schema）
