# Design: Codex guard のリダイレクト write 検出をターゲット基準にする (Issue #37)

**Date:** 2026-06-07
**Status:** Approved
**Tier:** 1
**Closes:** Issue #37

## 概要

`codex-sdd-guard.sh` の `looks_like_write_bash()` は、リダイレクトを
`(^|[^0-9])>>?([^&]|$)` で判定している。`>` の直前が数字だと除外するため
`2>/dev/null` のような read を救える一方、`echo x 1> file.py` のような
**明示 fd 付きの書き込み**も検出から漏れる（#36 で導入された挙動後退）。

fd 番号によるヒューリスティックをやめ、「**リダイレクト先が実ファイルなら write、
`/dev/null` と fd 複製（`2>&1`, `>&2`）は無視**」というターゲット基準の判定に置き換える。
これは read/write の意味そのものであり、検出漏れ（`1>file`）と
誤検知（`2>/dev/null`）の両方を同時に解消する。

## 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `integration/hooks/codex-sdd-guard.sh` | `looks_like_write_bash()` のリダイレクト検出のみ置換 |
| `tests/test_codex_sdd_guard.py` | リグレッションテスト追加 |

## 検出ロジック

第1 grep（`apply_patch` / `sed -i` / `perl -pi` / `rm`・`mv`・`cp`・`touch`）は維持。
リダイレクト検出を「安全なリダイレクトを除去 → 残った `>` があれば write」に変更する。

```bash
looks_like_write_bash() {
  printf '%s' "$command" | grep -Eq '(apply_patch|\bsed\b[^\n]*[[:space:]]-i|\bperl\b[^\n]*[[:space:]]-pi|\b(rm|mv|cp|touch)\b)' && return 0
  # リダイレクト先が実ファイルなら write。/dev/null と fd 複製 (2>&1, >&2) は無視。
  local redir
  redir="$(printf '%s' "$command" | sed -E 's#[0-9]*>>?[[:space:]]*/dev/null##g; s#&>>?[[:space:]]*/dev/null##g; s#[0-9]*>&[0-9-]*##g')"
  printf '%s' "$redir" | grep -Eq '>>?'
}
```

- `[0-9]*>>?[[:space:]]*/dev/null` → `>/dev/null`, `2>/dev/null`, `>>/dev/null` を除去
- `&>>?[[:space:]]*/dev/null` → `&>/dev/null`（stdout+stderr）を除去
- `[0-9]*>&[0-9-]*` → `2>&1`, `>&2`, `1>&2`, `>&-` の fd 複製を除去
- 除去後に `>`/`>>` が残れば実ファイルへの書き込み → write

`sed` の区切りに `#` を使い `/dev/null` のスラッシュをエスケープ不要にする。

## 受け入れ条件

1. `echo x 1> app.py`（明示 fd 書き込み）→ write 検出 → primary checkout から deny
2. `echo x > app.py`（fd なし）→ 引き続き write 検出（リグレッション防止）
3. `cmd 2> out.py`（stderr を実ファイルへ）→ write 検出
4. `sed -n '1,5p' app.py 2>/dev/null` → write 扱いしない（既存テスト green 維持）
5. `cmd ... 2>&1` を含む read → write 扱いしない
6. apply_patch / worktree 判定は無変更（既存テスト green）

## スコープ外

- `sdd-guard.sh`（Claude 版）の同種対応 → Issue #39 で別途検討
- テストカバレッジの全面補強 → Issue #38
- クォート内の `>`（例 `echo "a > b"`）の誤検知 → 既存の制約であり本 issue の対象外
  （`bash_paths` がソース拡張子のみ抽出するため実害は reminder 止まり）
