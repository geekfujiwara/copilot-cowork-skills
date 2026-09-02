# Scoring and Ranking

## スコア

開始前に式を定義し、画面で説明する。基本点、正確性、時間、ヒント、連続正解などの要素には上限・下限を設ける。端末時刻だけを信頼した競争ランキングや、リロードで無制限加点できる設計を避ける。

## ローカルランキング

既定はブラウザの `localStorage` に保存する。保存項目は、schemaVersion、gameId、runId、displayName、score、maxScore、completedAt、durationMs、breakdown、contentVersionとする。メール、社員ID、自由記述を既定で保存しない。

## JSON

エクスポートは次の形式とし、ファイル名は `game-scores-<date>.json` とする。

```json
{
  "schemaVersion": 1,
  "gameId": "sample-game",
  "exportedAt": "2026-01-01T00:00:00Z",
  "entries": []
}
```

インポート時はJSON構文、schemaVersion、gameId、型、得点範囲、日時、重複runId、件数上限を検証する。不正行を黙って採用しない。全消去には確認画面を置く。

実装時の基準は `score-schema.example.json` を参照する。

## 共有ランキング

静的HTMLだけでは利用者間の同期や改ざん防止はできない。共有が必要なら、組織承認済みの認証、API、データストアを使い、サーバー側でスコアを再検証する。表示名、保持期間、削除、モデレーション、同点順位、オフライン時の扱いを決める。秘密情報をクライアントへ埋め込まない。
