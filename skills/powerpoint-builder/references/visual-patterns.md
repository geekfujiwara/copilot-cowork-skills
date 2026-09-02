# PowerPoint Visual Patterns

ブランドテンプレートの指定がない場合は、このページを既定デザインとして使う。色、余白、画像スタイルを資料全体で統一し、ビジネス要件とスライドの主張に合わせて内容だけを変える。

## 1. 共通ライト・ダークデザイン

### Palette

| 用途 | Hex |
|---|---|
| 本文ページ背景 | `F5F7FB` |
| カード | `FFFFFF` |
| 罫線・区切り | `E4E7EF` |
| 特別ページ下地 | `000000`。必要に応じ `1E2761` を重ねる |
| 主色 | `1E2761` |
| アクセント | `0F6CBD` |
| 補助テキスト | `616A82` |
| 補助アクセント | `8FB3E0` |
| 本文 | `3A4A6B` |
| 淡い線・未参画 | `C7DBF5` |
| 淡い面 | `EAF1FB` |

新しい色を安易に追加しない。状態は色だけでなくラベルでも示す。

### Typography

- 全テキストは `Yu Gothic UI` を明示する。
- 本文は原則14pt以上。ページタイトル24〜28pt、セクション見出し16〜18pt。
- 14pt未満を許すのは出典・引用と、図を破綻させる小さな図中ラベルだけ。
- 文言が収まらない場合はフォントを縮小せず、本文を短くするかスライドを分ける。
- 文字と背景のコントラスト比は4.5:1以上を目標にする。

### Page types

本文ページは `F5F7FB`。表紙、章扉、Appendix扉、クロージングは濃色のままにする。すべてのページを同じカード配置にせず、主張に合う構成を選ぶ。

## 2. カード内イラスト

3カラムカードでは、画像を各カード上部の全幅へ配置する。画像は生成AIで作り、カード内の説明を視覚化する。

### 16:9 EMU layout

```text
L=457200
FW=11247120
GAP=200000
CW=(FW-2*GAP)/3=3615706
Card y=1597999, h=4205287
Image y=card_y+80000, h=1355889, aspect=8:3
Navy footer y=6048632, h=561368
```

- 背景 `F5F7FB`、白いroundRectカード、枠 `E4E7EF`。
- カード上端の色帯は置かず、番号バッジだけをアクセントにする。
- Eyebrowは9pt、タイトル26pt、リード14pt、カード見出し16pt、本文14pt。
- 画像の下に番号円と見出し、区切線、本文を置く。

### Default illustration prompt

```text
Create a wide 8:3 presentation illustration for a business content card.
Business message: <CARD_MESSAGE>.
Scene: <SUBJECTS_AND_ACTION>.
Style: flat vector illustration, thin outline strokes, rounded stylized fictional
business figures, light background from #FFFFFF to #F5F7FB, palette limited to
navy #1E2761, blue #2F6FD0, and light blue #8FB3E0, small plant and desk props,
clean enterprise editorial design, generous white space.
Composition: all elements fully inside the frame, one clear focal action, readable
at small card size, balanced horizontal layout, no cropping at edges.
Do not include words, letters, numbers, logos, product marks, watermarks, charts,
or interface labels.
```

人物は架空の成人とし、実在人物、顧客、制服、名札を再現しない。生成後にカードへ配置して視覚確認し、被写体の切れ、文字らしき模様、崩れた手指を修正する。

## 3. セクション区切りの箱庭背景

表紙、セクション扉、Appendix扉、クロージングだけに使用する。本文や図表主体のページには使わない。

- 下地は濃紺 `101E4B`。
- 被写体を右、見出しを左に置く。
- 画像の原寸比を保ち、16:9へ引き伸ばさない。
- 左端に濃紺から透明へのグラデーションを重ね、境界をなじませる。
- ページごとに被写体、時間帯、角度を変え、同じ画像を再利用しない。

### Default section prompt

```text
Create an isometric 3D miniature diorama island for a professional PowerPoint
section divider. Business theme: <SECTION_THEME>. Scene: <BUSINESS_SCENE>.
Style: soft rounded clay-like 3D render on a plain deep navy #101E4B background,
tiny fictional adult professionals, restrained plants and architectural details,
warm window lights, glowing cyan pathways, a few floating rounded abstract panels,
premium enterprise quality, coherent isometric perspective.
Composition: place the entire island on the RIGHT side; preserve the LEFT 48 percent
as quiet deep-navy negative space for a large heading; keep every object inside the
frame; landscape 16:9; seamless background suitable for a left-to-right gradient blend.
No words, letters, numbers, logos, product marks, readable screens, watermarks,
borders, or recognizable copyrighted characters.
```

ビジネス要件を `<SECTION_THEME>` と `<BUSINESS_SCENE>` に具体化する。画像生成後、左側に白い見出しとシアンの強調語をPowerPointテキストで配置する。

## 4. 階層・成熟度図

組織階層または段階的な展開状況は、画像ではなくPowerPointネイティブ図形で作る。`scripts/hierarchy_diagram.py` の `add_hierarchy_diagram()` を使う。

### Geometry

```text
CW=2606040
inner=card_x+182880
IW=2240280
BH=274320
BOXW=685800
GAP=91440
```

- 本部箱: `x=card_x+525780`, `y=Y0`, `w=1554480`, `h=BH`。
- 縦ステム: 本部中心から横バーまで。線幅相当 `9525`。
- 横バー: 左端事業部箱中心から右端事業部箱中心まで。
- 事業部箱3個: `x=inner+j*(BOXW+GAP)`, `y=Y0+BH+182880`。
- キャプション: `y=Y0+BH*2+228600`, `w=IW`。

| 状態 | 塗り | 線 | 文字 |
|---|---|---|---|
| 未参画 | `F5F7FB` | 破線 `C7DBF5` | なし |
| 育成中 | `EAF1FB` | `C7DBF5` | `1E2761`、8pt太字 |
| 稼働 | `0F6CBD` | `0F6CBD` | 白、8pt太字 |

STEP1は全て未参画、STEP2は1つ育成中、STEP3は1つ稼働、STEP4は3つ稼働。STEP1の接続線は `AEBCD4`、他は `0F6CBD`。Pythonで全図形を一括生成し、保存後に1度だけ描画して確認する。図形ごとに保存・再描画を繰り返さない。

## 5. ロングテール分析

ロングテールの説明は画像化せず、PowerPointネイティブ図形と曲線で作る。

### Layout

- 16:9、背景 `F5F7FB`、左右余白 `457200` EMU。
- タイトル `y=228600`, `h=502920`, 20pt太字。前半 `1E2761`、強調部 `0F6CBD`。
- サブタイトル `y=768096`, 14pt、`3A4A6B`、1〜2行。
- 本体カード `y=1335024`, `h=3008376`、白roundRect、線 `E4E7EF` 0.75pt。
- X/Y軸は細線と軸ラベル。Y軸ラベルは90度回転。
- 1本の曲線でロングテールを表し、中央に破線の分割線を置く。
- 左右領域を淡いブルーで分け、各領域に青いバッジと補足ノートを置く。
- 下部に左右対称の白カード2枚を配置する。

装飾専用オブジェクトを置かない。軸、領域、バッジ、解説はすべて主張の理解に必要な情報だけにする。

## Final visual review

必ず全ページを画像化して確認し、最低1回ブラッシュアップする。特に、生成画像と文字の干渉、カード内画像の切れ、区切りページ左側の余白、図形の揃え、10〜14pt文字の可読性、低コントラストを確認する。
