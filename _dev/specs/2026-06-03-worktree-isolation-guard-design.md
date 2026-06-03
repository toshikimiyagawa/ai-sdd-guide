# Design: Worktree Isolation Guard (Issue #27)

**Date:** 2026-06-03
**Status:** Approved
**Closes:** Issue #27

## 概要

`sdd-guard.sh` と `codex-sdd-guard.sh` に、プライマリ checkout からのソース編集を拒否するガードを追加する。
git worktree で作成したリンク worktree のみからソース編集を許可することで、
「parallel feature は必ず feature-per-worktree」というルールをフック層で強制する。

## 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `integration/hooks/sdd-guard.sh` | worktree 分離チェックを追加 |
| `integration/hooks/codex-sdd-guard.sh` | 同上（`deny` 関数で JSON 出力） |
| `integration/hooks/README.md` | 新規作成：動作説明・worktree 手順・escape hatch・Codex `/hooks` trust |

## 検出ロジック

```bash
git_dir="$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P || true)"
git_common="$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P || true)"
superproject="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"

if [ "$git_dir" = "$git_common" ] && [ -z "$superproject" ]; then
  # primary checkout (not a worktree, not a submodule) — deny
fi
```

- `git_dir == git_common` → リンク worktree ではない
- `superproject` が空 → git submodule でもない
- → プライマリ checkout と判断してブロック

## Escape hatch

```bash
SDD_ALLOW_MAIN_WORKTREE=1 <tool>
```

環境変数 `SDD_ALLOW_MAIN_WORKTREE=1` が設定されている場合はガードをスキップする。
メンテナンス作業（フック自体の更新など）に使用する。

## チェックの配置

既存の exempt-path チェック（*.md, specs/, docs/, .sdd/ など）の**後**、state.json 読み取りの**前**に挿入する。
これにより docs/specs のファイルはプライマリ checkout でも読み書き可能のまま。

## 受け入れ条件

1. プライマリ checkout からのソース編集はフックにブロックされる
2. リンク worktree からのソース編集は通常どおり通過する
3. git submodule 内ではこのガードが発動しない（誤検知しない）
4. `SDD_ALLOW_MAIN_WORKTREE=1` 設定時はガードをスキップする
5. `integration/hooks/README.md` が作成され、動作説明・worktree 作成手順・escape hatch・Codex `/hooks` trust 手順を含む

## スコープ外

- `skill-reminder.sh` / `codex-skill-reminder.sh`：これらは非ブロッキングな reminder なので worktree チェック不要
- `sdd-check.yml`（CI）：CI は worktree の概念を持たないため対象外
