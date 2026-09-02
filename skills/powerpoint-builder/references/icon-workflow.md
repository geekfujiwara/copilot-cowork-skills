# Microsoft Architecture Icon Workflow

## Source and terms

[MS Icons](https://msicons.com/) はMicrosoftアーキテクチャアイコンを検索・プレビュー・取得できるコミュニティ運営サイトで、Microsoft公式サイトではない。アイコンはMicrosoftの所有物であり、Azure、Microsoft Entra、Microsoft 365、Power Platformなど、各セットの公式利用条件が適用される。

公式条件では、対象アイコンをアーキテクチャ図、トレーニング資料、ドキュメントで利用できる。製品名をアイコンの近くに表示し、切り抜き、反転、回転、形状変更、色変更、歪みを行わない。Microsoft製品アイコンを自社製品・サービスの表現に使わない。セットによってはマーケティング用途が禁止されるため、提案資料や外部向け資料では対象セットの条件を個別に確認する。

## Plan icons before download

スライド構成確定後、次を `working/icon-plan.json` に記録する。

```json
{
  "icons": [
    {
      "id": "service-a",
      "product_label": "<正式な製品名>",
      "purpose": "構成図の処理サービス",
      "slide": 5,
      "detail_page": "https://msicons.com/<icon-page>",
      "source_url": "https://msicons.com/icons/<category>/<file>.svg",
      "official_terms_url": "https://learn.microsoft.com/<official-terms-page>",
      "local_path": "working/images/icons/service-a.svg",
      "format": "svg"
    }
  ]
}
```

- 同じ概念へ複数アイコンを割り当てない。
- 製品アイコンが不要な一般概念はPowerPointのネイティブ図形で表す。
- アイコン名だけで製品を推測せず、詳細ページの名称とカテゴリを確認する。
- 必要なアイコンだけを取得し、アイコン集全体をスキルへ再配布しない。

## Download to a local image folder

1. MS Iconsで候補を検索し、詳細ページを開く。
2. 所属する製品セットのMicrosoft公式利用条件を読む。
3. 用途が許可範囲内であることを確認する。
4. SVGまたは必要解像度のPNGを `working/images/icons/` に保存する。
5. `scripts/prepare_icons.py working/icon-plan.json` でURL、形式、実在を検証する。
6. PPTX生成コードでは `local_path` のみを参照する。

SVGでPowerPoint互換性に問題がある環境では、元SVGを変形せずPNGへ変換する。縦横比を維持し、背景色や余白を勝手に変更しない。

## Presentation placement

- 製品名をアイコンの近くに編集可能テキストで表示する。
- 同じ階層のアイコンは同じ表示サイズにするが、縦横比は保持する。
- アイコン間の接続線、矢印、境界はPowerPoint図形で描く。
- 低コントラストになる場合はアイコン自体を改変せず、背面に中立色のカードを置く。
- 出典スライドまたはノートに詳細ページと公式条件URLを記録する。

## Failure handling

利用条件、正式名称、ファイル形式、取得元を確認できない場合はダウンロードしない。アイコンなしのネイティブ図形へ切り替え、「要確認」と報告する。ログイン、アクセス制御、利用条件を迂回しない。
