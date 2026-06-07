# Design: codex-sdd-guard.sh テストカバレッジ補強 (Issue #38)

**Date:** 2026-06-07
**Status:** Approved
**Tier:** 1
**Closes:** Issue #38

## 概要

`tests/test_codex_sdd_guard.py` の未カバー分岐を埋める。挙動変更は無く、
既存挙動を pin するリグレッションテストの追加のみ。

issue #38 のチェック項目のうち「Bash write の positive 検出」は #40(PR #40)で
追加済み(`test_bash_plain_redirect_write_is_detected` 他)。本対応は残り4ケースを扱う。

## 追加テスト

| テスト | 検証する分岐 | 期待 |
|---|---|---|
| tier 0 許可 | `[ "$tier" = "0" ] && continue`(phase 不問) | linked worktree + tier0 → allow |
| tier 未設定 deny | `[ -z "$tier" ]` → "Tier is not classified" | linked worktree + tier 欠如 → deny |
| workdir 無し相対パス fallback | `base_dir="${tool_workdir:-$invocation_root}"` | 相対パス + workdir 無し + cwd=primary → invocation_root=primary に解決 → deny |
| 複数 repo の roots ループ | worktree-block ループが root 集合をまたぐ | 1パッチが worktree と primary の両方を触る → 1つでも primary なら deny |

## 受け入れ条件

1. 上記4テストを追加し、全テスト(既存8 + 新規4 = 12)が green
2. プロダクションコード(`codex-sdd-guard.sh`)は無変更

## スコープ外

- `sdd-guard.sh`(Claude版)のテスト → #39 の対応次第
- ヘルパ(`_make_repo`)の大幅リファクタ → 必要最小限の拡張に留める
