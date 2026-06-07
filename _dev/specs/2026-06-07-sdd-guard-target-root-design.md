# Design: sdd-guard.sh のroot解決を編集対象パス基準にする (Issue #39)

**Date:** 2026-06-07
**Status:** Approved
**Tier:** 2
**Closes:** Issue #39

## 背景・調査結果

`sdd-guard.sh`（Claude版）は worktree 判定と state 読み取りをともに **cwd 基準**で行い、
編集対象 `file_path` のリポジトリを見ていない。#36 が codex 版で直したのと同じ構造の不具合。

実機再現（`integration/hooks/sdd-guard.sh`）:

| ケース | cwd | 編集対象 | 正しい挙動 | 現状 |
|---|---|---|---|---|
| 1 誤検知 | primary | linked worktree のファイル | 許可 | deny (exit 2) ❌ |
| 2 バイパス | linked worktree | primary checkout のファイル | deny | 許可 (exit 0) ❌ |

ケース2は **worktree 分離ガードの回避**に直結する（worktree から起動して絶対パスで
primary を編集すると素通りする）。

## 修正方針（#36 の移植・単一パス版）

`file_path` から対象リポジトリ root を解決し、その root に対して判定する。

1. `file_path` を絶対化（相対ならフック入力の `cwd` / `PWD` 基準）
2. 存在する親ディレクトリで `git -C <dir> rev-parse --show-toplevel` → `target_root`
   （解決不能なら `invocation_root` にフォールバック）
3. worktree 判定を `git -C "$target_root" rev-parse --git-dir/--git-common-dir/--show-superproject-working-tree` で実行
4. state を `"$target_root/.sdd/state.json"` から読む

codex 版（#36）と同じヘルパ（`resolve_path` / `existing_parent` / `git_abs_path` /
`repo_root_for_path`）を用い、両フックの解決ロジックを揃える。Claude の Edit/Write は
単一 `file_path`（通常は絶対パス）なので、codex のマルチパス/`workdir` 処理は不要。

出力契約は現状維持: 拒否は stderr + `exit 2`（Claude Code の PreToolUse ブロック契約）。

## 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `integration/hooks/sdd-guard.sh` | cwd 基準 → 対象パス基準の root 解決に置換 |
| `tests/test_sdd_guard.py` | 新規。exit code + stderr ベースのリグレッションテスト |

## 受け入れ条件

1. ケース1（cwd=primary, 対象=linked worktree）→ 許可（exit 0）
2. ケース2（cwd=linked worktree, 対象=primary checkout）→ deny（exit 2, worktree メッセージ）
3. 同一 worktree 内の正常編集（tier 設定済み・phase=implement）→ 許可
4. tier 未設定 → "Tier が未分類" deny / Tier 0 → 許可（対象 root の state 基準）
5. exempt path（`*.md` / `specs/` / `docs/` / `.sdd/`）→ 常に許可
6. `SDD_ALLOW_MAIN_WORKTREE=1` → 引き続きバイパス
7. `file_path` 無し（Bash 等）→ 現状どおり exit 0

## スコープ外

- Bash コマンドの write 検出（Claude版は元々 `file_path` のみ対象。別issue相当）
- codex 版の挙動変更（#36 で対応済み）
- git submodule 環境の細かな扱い（`--show-superproject-working-tree` の既存判定を踏襲）
