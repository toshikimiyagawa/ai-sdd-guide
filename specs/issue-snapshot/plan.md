# Plan: issue-snapshot

## 目的

Issue #53 の scope に従い、GitHub Issue 本文の snapshot 生成と validator による
Issue AC traceability 検査を追加する。

## 実装手順

### T1. Snapshot schema

- `orchestration/schema/issue-snapshot.schema.json` を追加する。
- `issue`, `url`, `fetched_at`, `raw_body`, `body_hash`, `stable_acs` を required にする。
- `body_hash` は `^[0-9a-f]{64}$` に制約する。
- `stable_acs[].id` は `^[1-9][0-9]*-AC[1-9][0-9]*$` に制約する。
- top-level と nested entry の `additionalProperties` を `false` にする。

### T2. Snapshot CLI

- `integration/ci/sdd-issue-snapshot.sh` を追加する。
- 必要なら `integration/ci/sdd-issue-snapshot.py` に実装を置く。
- CLI は Issue 番号と feature 名を受け取り、`specs/<feature>/issue-snapshot.json` を書く。
- `gh issue view <N> --json body,title,url` で `body` と `url` を取得する。
- `## 受入条件` section の markdown task-list item を stable AC として抽出する。
- `raw_body` の UTF-8 文字列に対する SHA-256 を `body_hash` に保存する。
- テスト用に local body input を受け取れる経路を用意する。

### T3. Validator checks

- `integration/ci/sdd-validate.py` に issue snapshot load/schema check を追加する。
- Tier 2 feature では snapshot missing を validation error にする。
- `raw_body` と `body_hash` を検査する。
- `stable_acs` の ID が `issue` と配列順に一致することを検査する。
- `traceability.json entries[].issue_ac` と snapshot の AC ID set を比較する。
- snapshot 側に未追跡 AC がある場合も、traceability 側に存在しない AC 参照がある場合も error にする。

### T4. Tests and fixtures

- schema test を追加する。
- CLI test を追加する。
- validator の negative tests を追加する。
- #53 自身の `issue-snapshot.json` を生成し、`traceability.json` と一致させる。

## 実行する検証

```sh
PATH=/tmp/ai-sdd-guide-test-venv/bin:$PATH /tmp/ai-sdd-guide-test-venv/bin/pytest -q
```
