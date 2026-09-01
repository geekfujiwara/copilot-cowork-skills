#!/usr/bin/env python3
"""
extract_chat_image_refs.py — Teams 会議チャットのメッセージ JSON から
画像（hostedContents）付きメッセージを抽出し、ダウンロード用の Graph パスを出力する。

汎用イベント開催レポート用。アプリ早作り対決のスクショなど、各参加者がチャットに
投稿した画像を後続記事用に収集するために使う。

前提:
  会議チャットの実 ID（19:meeting_...@thread.v2）で messages を取得し、spill JSON を渡す。
    QueryGraph path: /chats/{chatId}/messages
    query_params: {"$top":"50","$select":"id,from,body,attachments,createdDateTime"}
  ページングは $skiptoken の base64 をそのまま渡す（$select は外す）。

使い方:
  python extract_chat_image_refs.py --chat-id '19:meeting_...@thread.v2' \
      --files /workspace/.mcp-results/p1.json /workspace/.mcp-results/p2.json

出力:
  画像付きメッセージごとに、投稿者名・作成時刻・QueryGraph で叩く $value パスを表示。
  各 $value パスを QueryGraph(path=..., query_params={}) で叩くと
  画像が grounding/downloads/<hostedId>.png に保存される。
"""
import json, re, argparse


def load_spilled(path):
    raw = open(path, encoding="utf-8").read()
    obj = json.loads(raw, strict=False)
    if isinstance(obj, dict) and "result" in obj:
        obj = json.loads(obj["result"]["content"][0]["text"], strict=False)
    return obj.get("value", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat-id", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    args = ap.parse_args()

    n = 0
    for f in args.files:
        for m in load_spilled(f):
            body = (m.get("body") or {}).get("content", "") or ""
            hosted = re.findall(r'hostedContents/([^/"]+)/\$value', body)
            if not hosted:
                continue
            frm = ((m.get("from") or {}).get("user") or {}).get("displayName", "?")
            ts = m.get("createdDateTime", "")
            for h in hosted:
                n += 1
                print(f"# {frm} | {ts}")
                print(f"/chats/{args.chat_id}/messages/{m['id']}/hostedContents/{h}/$value")
    print(f"\n# 合計 {n} 画像。各行を QueryGraph(path=..., query_params={{}}) で取得。")


if __name__ == "__main__":
    main()
