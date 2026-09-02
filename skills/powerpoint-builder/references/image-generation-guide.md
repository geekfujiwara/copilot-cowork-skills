# Image Generation Guide

## Plan before generation

画像はスライドの主張を補強する場合だけ生成する。先に `working/asset-plan.json` へ次を記録する。

```json
{
  "assets": [
    {
      "id": "cover-background",
      "kind": "generated-background",
      "slide": 1,
      "purpose": "テーマと変革の方向性を伝える",
      "aspect_ratio": "16:9",
      "placement": "full-bleed",
      "negative_space": "left",
      "prompt_file": "working/prompts/cover-background.txt",
      "local_path": "working/images/generated/cover-background.png",
      "alt_text": "抽象的なデータの流れが奥へ続く背景"
    }
  ]
}
```

同じ意味の画像を複数スライドへ繰り返さない。表紙、セクション扉、概念説明、人物や利用場面など、画像が担う役割を区別する。

## Default visual families

ブランド指定がない場合は、用途に応じて2つの視覚ファミリーを使い分ける。寸法、色、配置の完全な仕様は `visual-patterns.md` を参照する。

- 本文カード・挿絵: 白〜淡灰背景、紺・青・淡青に限定したフラットベクター、細線、丸みのある架空のビジネス人物、8:3。
- 表紙・章扉・Appendix・クロージング: 濃紺背景、右寄せのアイソメトリック3D箱庭、左側を文字用の余白とする16:9。

ブランドテンプレートが指定された場合は、その色・質感・写真ルールを優先する。画像生成モデルへ内部のブランドガイドそのものを送らず、許可された視覚属性だけを抽象化する。

## Section background prompt

```text
Create an isometric 3D miniature diorama island for a professional PowerPoint
section divider. Business theme: <SECTION_THEME>. Scene: <BUSINESS_SCENE>.
Style: soft rounded clay-like 3D render on a plain deep navy #101E4B background,
tiny fictional adult professionals, restrained plants and architecture, warm window
lights, glowing cyan pathways, a few floating rounded abstract panels, coherent
isometric perspective.
Composition: place the entire island on the RIGHT side; preserve the LEFT 48 percent
as quiet deep-navy negative space for a large heading; keep every object inside the
frame; landscape 16:9; seamless background for a left-to-right gradient blend.
No words, letters, numbers, logos, product marks, readable screens, watermarks,
borders, or recognizable copyrighted characters.
```

背景には細かな文字や複雑なダッシュボードを描かせない。暗いオーバーレイを重ねる場合も、主題が消えない透明度にする。

## Card illustration prompt

```text
Create a wide 8:3 presentation illustration for a business content card.
Business message: <CARD_MESSAGE>. Scene: <SUBJECTS_AND_ACTION>.
Style: flat vector illustration, thin outline strokes, rounded stylized fictional
business figures, light background from #FFFFFF to #F5F7FB, palette limited to
navy #1E2761, blue #2F6FD0, and light blue #8FB3E0, small plant and desk props,
clean enterprise editorial design, generous white space.
Composition: all elements fully inside the frame, one clear focal action, readable
at small card size, balanced horizontal layout, no cropping at edges.
No words, letters, numbers, logos, product marks, watermarks, charts, or interface labels.
```

ラベル、数値、矢印は画像に生成せず、PowerPointの編集可能なテキストと図形で重ねる。

## Human scenario prompt additions

人物が必要な場合は、役割、行動、環境のみを指定し、実在人物や属性を推測しない。多様性は自然に表現し、誇張した感情、固定観念、個人を特定できる制服や名札を避ける。

```text
Depict fictional adult professionals collaborating naturally in a contemporary workplace.
Use non-identifiable faces, realistic anatomy and hands, respectful neutral expressions,
and no badges, names, company logos, or readable screens.
```

## Review loop

1. 画像を開き、主題、余白、縦横比、解像度を確認する。
2. 文字、ロゴ、透かし、不自然な物体、崩れた人物、誤解を招く構成を探す。
3. 問題点をプロンプトへ具体的に反映して再生成する。
4. PPTXへ配置し、トリミングと文字コントラストを確認する。
5. 画像の意味を代替説明またはスピーカーノートへ残す。

生成画像であることが判断に影響する場合は、スライドまたはノートで明示する。
