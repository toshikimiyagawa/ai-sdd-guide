# Spec: negative-tests

Issue: #47 (parent: #43)
Tier: 2

## 目的

`sdd-validate.py` の各チェックが失敗パターンを確実に検出することを、fixture ベースの RED/GREEN テストで証明する。

## Acceptance Criteria

- SAC-1: `tests/fixtures/fixture-*/` 配下に 14 個の negative fixture ディレクトリが存在する（core 8 個、snapshot 3 個、evidence 3 個）
- SAC-2: 各 negative fixture に対して `bash integration/ci/sdd-validate.sh --root tests/fixtures/fixture-<name>` が exit 1 を返し、対応するエラー文字列を stderr に出力する
- SAC-3: 各 fixture の valid 版（`fixture-<name>-valid/`）に対して同コマンドが exit 0 を返す
- SAC-4: `tests/test_negative_fixtures.py` が上記 RED/GREEN を自動検証し、既存の CI pipeline で実行される
- SAC-5: 各 negative fixture の `README.md` に「再現パターン・対応チェック番号・実行コマンド」が記載されている
