# 異常系フロー（Error Flows）

正常系（SKILL.md）で詰まったときの検知と対処をここに集約する。多くはビルトイン
`skills` スキルのスクリプト（`${COWORK_BUILTIN_SKILLS_ROOT}/skills/scripts/`）で
検知できる。`BUILTIN` をそのパスとして表記する。環境変数は `.env.example` を参照する。

---

## 1. 名前が不正 / ビルトインと衝突

- **検知**: `scaffold_skill.py` が終了コード 2 ＋ `ERROR: 名前 '...' が不正です` /
  `... はビルトインスキルと衝突します`。名前規則は `^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$`。
- **対処**:
  - kebab-case（英数字・ハイフン・アンダースコア・ドット、先頭は英数字、最大 64 文字）に直す。
  - `pdf` / `docx` / `skills` 等のビルトイン名は避ける。意図的に上書きする場合のみ、
    別名にせず SKILL.md の description に「This skill OVERRIDES the built-in X」と明記する
    （deck スキル が pptx を上書きするのと同じ方式）。
  - **name とディレクトリ名は必ず一致**させる。不一致は無言の発見失敗になる。

## 2. スキル数が 50 件の上限に到達

- **検知**: `scaffold_skill.py` が `スキル数が上限 50 に達しています`。
  事前確認はスクリプトの件数チェックを使う。手作業で数えない。
- **対処**: 古いスキルをビルトイン skills スキルの Delete 操作で削除してから再実行
  （削除はビルトイン `skills` スキルの確認ゲートに委譲する）。

## 3. YAML パースエラー（frontmatter）

- **検知**: `validate_skill.py` の `yaml_parseable` が FAIL、または
  `frontmatter_delimiters` FAIL。
- **対処**:
  - description にコロン `:` を含めるなら、リテラルブロックスカラー `|` を使う
    （scaffold 雛形は既に `description: |` 形式）。
  - `---` 区切りが本文先頭に正しく 2 つあるか確認。インデントはスペース（タブ不可）。

## 4. 構造検証 FAIL（validate_skill.py）

- **検知**: `python $BUILTIN/validate_skill.py {SKILL.md}` の `passed: false`。
  個別チェック（file_size / name_dir_match / description_present / cowork_block 等）を見る。
- **対処**: FAIL したチェックを名指しで修正してから採点へ進む。採点（score）の前に
  構造（validate）を必ず通すこと。

## 5. スコアが MVB（70）未満

- **検知**: `score_skill.py --json` の `total < 70` または `mvb_pass: false`、
  あるいは Safety FAIL。
- **対処**: 低い次元を優先的に補強する（best-practices の 4 次元）：
  - Trigger Clarity: トリガー句を 5 句以上＋除外行
  - Instruction Specificity: 番号付きワークフロー＋具体ツール名＋出力フォーマット
  - Scope Boundaries: 「When NOT to Use」で別スキルへ委譲
  - Robustness: Guardrails 3 つ以上＋データ欠落時のフォールバック＋破壊的操作前の確認
  - **過学習しない**: 失敗した逐語句ではなく、広い概念を足す。
  - 深い最適化はビルトイン skills スキルの「Optimize（検証ゲート付き）」へ委譲してよい。

## 6. コンフリクト / コエグジスタンス（他スキルのトリガーを奪う）

- **検知**: `python $BUILTIN/conflict_scan.py --plugin {dir} --json`。
  内部（バンドル内）／外部（ビルトイン対）の重なりを HIGH/MEDIUM で報告。
- **対処**: ほぼ全て同じ — 広い方のスキルに
  「Do NOT use for X — use <別スキル> instead」の委譲行を足す。スキャナはこれを
  RESOLVED として扱う。本スキル自身も「検証・採点・管理はビルトイン skills へ委譲」と
  明記してコエグジスタンスを回避している。

## 7. セキュリティスキャン FAIL（バンドルコード／プロンプトインジェクション）

- **検知**: `python $BUILTIN/security_scan.py {dir} --json` の FAIL
  （bandit ＋ プロンプトインジェクション検出: 命令上書き・外部ビーコン・資格情報参照・
  不透明 base64・ネットワーク送信）。
- **対処**:
  - 自作スキル: 該当コード／文言を除去して再スキャン。
  - 第三者バンドル: FAIL は「インストール非推奨」の判断材料であり、修正提案ではない。
  - **検証のためにバンドルのコードを実行しない**（scan/validate は静的設計）。
  - PASS は安全の保証ではない（正規表現トリップワイヤ。同義表現や homoglyph は回避し得る）。

## 8. バンドルコード／参照リンク切れ（validate_assets.py）

- **検知**: `python $BUILTIN/validate_assets.py {dir}` が Python 構文／import 解決／
  SKILL.md 内の `references/…`・`scripts/…` リンク切れを FAIL 報告。
- **対処**: 構文・import を直し、SKILL.md のリンク先が実在ファイルを指すように修正。
  本スキルは scaffold で生成した相対リンクのみを使う。

## 9. 書き戻し（OneDrive 同期）の遅延・未反映

- **検知**: 作成直後に OneDrive 側へ出てこない、別セッションで見えない。
- **対処**: 書き戻しは非同期。FUSE マウント書き込み → rclone フラッシュ（約 5 秒）→
  OneDrive レプリケーション（約 30 秒）。**約 35 秒で反映**とユーザーに伝え、即時を約束しない。
  パーソナル指示（copilot-instructions.md）の変更は次セッションから有効。

## 10. ディレクトリが既に存在

- **検知**: `scaffold_skill.py` が `'...SKILL.md' は既に存在します`。
- **対処**: 別名にするか、上書き意図が明確なら `--force` を付けて再実行。既存スキルの
  「改善」が目的なら scaffold ではなくビルトイン skills スキルの Optimize を使う。
