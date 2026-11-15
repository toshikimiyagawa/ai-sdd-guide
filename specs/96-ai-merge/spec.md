# Spec: 96-ai-merge

- Tier: 2
- Feature slug: 96-ai-merge
- Issue: #96
- Traceability: [traceability.json](traceability.json)

## 背景 / 意図

#89 で人間の関与を「最初の質問・問い合わせ・PR のレビューとマージ」の 3 つに絞った。しかし PR ができたあとも、人間がマージ・作業ブランチや worktree の削除・手元の main の更新のために戻ってくる必要がある。

最初の質問に答えたら、あとは PR のマージと後片付けまで AI が行う。どうしても判断が要るものだけ、途中で問い合わせる。人間はマージのあとで、結果の報告と PR 本文の「AI の判断」を見る。

方針（2026-11-15、人間と確認済み）: guide の既定にする（リポジトリごとの切り替えは作らない）。Tier 2。

## 用語と規則

### 人間が関わる場面

1. **最初の質問**: 今と同じ
2. **問い合わせ**: 「問い合わせの条件」に当たるときだけ。今と同じ
3. **結果の確認**: AI がマージと後片付けを終えて報告したあと、人間は報告と PR 本文の「AI の判断」を見る。直したいことがあれば新しい Issue にする

### 自律で進める範囲（今の 1〜9 の後半を置き換える）

8. push して PR を作る
9. CI の結果を待つ
10. マージの条件を満たしたら、AI が PR をマージする
11. 後片付けをする
12. 人間に結果を報告する

### マージの条件

次のすべてを満たすときだけマージする。

- CI のチェックがすべて通っている。CI が無いリポジトリでは、テストを手元で流して通っている
- `sdd-reviewer` が PASS を返している（Tier 0 は除く）
- PR がマージできる状態（競合が無い、必須のチェックが通っている）

満たせないときの扱い:

- CI が落ちたら、凍結した spec の範囲で直して push し直す。spec を変えないと直せず、条件 1・2 に当たるなら問い合わせる
- main が進んで競合したら、main を作業ブランチにマージして解き、テストと CI をやり直す（force push はしない）
- ブランチ保護の必須レビューなど、権限が足りずマージできないときは問い合わせる（条件 6）。`--admin` などで保護を迂回しない

マージの方法は squash を使う。リポジトリが squash を許していなければ、許されている方法を使う。

### 後片付け

マージのあと、次を行う。

1. リモートの作業ブランチを消す（`gh pr merge --delete-branch` など）
2. worktree を使っていれば消す（`git worktree remove`）
3. 手元の作業ブランチを消す
4. 手元の main（既定ブランチ）を最新にする（fast-forward）

ボードのカードは、今と同じく PR のマージで Actions が done にする。

### 結果の報告

人間に次を報告する: PR の URL、マージしたコミット、PR 本文の「AI の判断」の要約、後片付けの結果。人間がその場にいなければ、Issue に同じ内容をコメントする（マージで Issue は閉じる）。

### 問い合わせの条件 5 の例外

「作業ブランチの push と PR の作成は除く」を、「作業ブランチの push、PR の作成、マージの条件を満たした PR のマージ、マージした作業ブランチとその worktree の削除は除く」にする。

### 決めたこと（AI の判断）

- **D1 マージの方法**: squash。このリポジトリの履歴が squash で、1 PR が 1 コミットになり取り消しやすいため
- **D2 Tier 0**: `sdd-reviewer` を通らないので、マージの条件から `sdd-reviewer` の PASS を除く。CI とマージできる状態は求める
- **D3 人間がマージしたいリポジトリ**: 切り替えは作らない。ブランチ保護で必須レビューを設定すれば、AI はマージできずに問い合わせる（条件 6）。この使い方を `docs/migration.md` に書く
- **D4 報告の置き場所**: その場にいればその場、いなければ Issue のコメント（問い合わせの仕方と同じ）
- **D5 版の名前**: `docs/migration.md` の節は `## v4.3: AI が PR のマージと後片付けまで行う（#96）`
- **D6 確かめ方**: どの受入基準も rules・文書・テンプレートを書いたものなので、差分で確かめる（`rules/core.md`、#95）。テストは足さない

## 受入条件

- [ ] SAC-1: `rules/core.md`・`rules/workflow.md`・`rules/issue-intake.md`・`orchestration/rules/orchestration.md` で、上の「人間が関わる場面」と「自律で進める範囲」が既定の流れになっている。「Never merge」「never merge」「The human reviews and merges」の記述が無い。`## PR decision log` は、人間がマージの後に確かめるためのものになっている。確かめ方: 差分（元 Issue: 96-AC1）
- [ ] SAC-2: `orchestration/rules/orchestration.md` に「マージの条件」と満たせないときの扱いがあり、ほかの rules はそこを参照する。確かめ方: 差分（元 Issue: 96-AC2）
- [ ] SAC-3: `orchestration/rules/orchestration.md` に「後片付け」の 4 手順と「結果の報告」がある。確かめ方: 差分（元 Issue: 96-AC3）
- [ ] SAC-4: `orchestration/rules/orchestration.md` の `## Escalation conditions` の 5 の例外が、上の「問い合わせの条件 5 の例外」になっている。確かめ方: 差分（元 Issue: 96-AC4）
- [ ] SAC-5: `templates/pr-body.md`・`integration/AGENTS.md.example`・`orchestration/integration/AGENTS-patch.md.example`・`README.md`・`docs/00-overview.md`〜`docs/04-issue-tracker.md` に「AI はマージしない」「人間がマージする」の記述が無く、新しい流れと矛盾しない。`docs/migration.md` の過去の版の節（v4 など）は当時の記録なので変えない。確かめ方: 差分（元 Issue: 96-AC5）
- [ ] SAC-6: `docs/migration.md` に D5 の節があり、AI がマージと後片付けまで行うようになったこと、マージの条件、人間がマージしたいリポジトリはブランチ保護の必須レビューで止められること（D3）、`AGENTS.md`（または `CLAUDE.md`）の「never merge」を見直すことが書かれている。確かめ方: 差分（元 Issue: 96-AC6）

## スコープ外

- マージを自動で行う CI（auto-merge の設定）。AI がその場で行う
- リポジトリごとの切り替えの設定（D3）
- 過去の `specs/` と `_dev/`、`docs/migration.md` の過去の版の節の書き換え
- `rules/repo-agent-routing.md`（このリポジトリの開発だけの規則で、もともと AI がマージを決める）
- CI・validator・guard・`sdd_state.py`・ボードの動作の変更

## 制約 / 前提

- `rules/` は英語で命令形・簡潔、`docs/`・テンプレートは日本語（`rules/conventions.md`）
- エージェントに依存しない書き方にする
- 書いた内容を確かめるだけのテストを足さない（#95）
