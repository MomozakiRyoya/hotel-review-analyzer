#!/usr/bin/env python3
"""
楽天API診断スクリプト
このスクリプトでAPIキーの問題を診断します
"""
import httpx
import json
from datetime import datetime

APP_ID = "fae4bbb0-3a2a-46e1-af75-f219fc34c107"

def test_api(api_name, url, params):
    """Test a specific Rakuten API endpoint."""
    print(f"\n{'='*60}")
    print(f"テスト: {api_name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"パラメータ: {params}")

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        print(f"ステータスコード: {response.status_code}")

        try:
            data = response.json()
            print(f"レスポンス:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])

            if "error" in data:
                print(f"\n❌ エラー: {data.get('error')}")
                print(f"   詳細: {data.get('error_description', 'N/A')}")
                return False
            else:
                print(f"\n✅ 成功！")
                return True

        except json.JSONDecodeError:
            print(f"レスポンス（テキスト）: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")
        return False

def main():
    """Run all API tests."""
    print("="*60)
    print("楽天API診断ツール")
    print("="*60)
    print(f"アプリケーションID: {APP_ID}")
    print(f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Test 1: Travel KeywordHotelSearch
    results['Travel_KeywordHotelSearch'] = test_api(
        "Travel API - KeywordHotelSearch",
        "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426",
        {
            "applicationId": APP_ID,
            "keyword": "東京",
            "hits": 1,
            "format": "json"
        }
    )

    # Test 2: Travel SimpleHotelSearch
    results['Travel_SimpleHotelSearch'] = test_api(
        "Travel API - SimpleHotelSearch",
        "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426",
        {
            "applicationId": APP_ID,
            "largeClassCode": "japan",
            "middleClassCode": "tokyo",
            "hits": 1,
            "format": "json"
        }
    )

    # Test 3: Ichiba Item Search (different API)
    results['Ichiba_ItemSearch'] = test_api(
        "楽天市場API - ItemSearch（比較用）",
        "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706",
        {
            "applicationId": APP_ID,
            "keyword": "ノートパソコン",
            "hits": 1,
            "format": "json"
        }
    )

    # Test 4: Books Total Search (different API)
    results['Books_TotalSearch'] = test_api(
        "楽天ブックスAPI - TotalSearch（比較用）",
        "https://app.rakuten.co.jp/services/api/BooksTotal/Search/20170404",
        {
            "applicationId": APP_ID,
            "keyword": "Python",
            "hits": 1,
            "format": "json"
        }
    )

    # Summary
    print("\n" + "="*60)
    print("診断結果サマリー")
    print("="*60)

    for api_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{api_name}: {status}")

    print("\n" + "="*60)
    print("診断結果の解釈")
    print("="*60)

    if all(results.values()):
        print("✅ 全てのAPIが正常に動作しています！")
        print("   → アプリケーションIDは有効です")

    elif results['Travel_KeywordHotelSearch'] or results['Travel_SimpleHotelSearch']:
        print("✅ Travel APIが動作しています！")
        print("   → 本システムで利用可能です")

    elif results['Ichiba_ItemSearch'] or results['Books_TotalSearch']:
        print("⚠️  他のAPIは動作しますが、Travel APIは失敗しています")
        print("   → Travel APIの利用申請が必要かもしれません")
        print("   → 楽天デベロッパーページで「Travel API」の利用を有効化してください")

    else:
        print("❌ 全てのAPIが失敗しています")
        print("   → アプリケーションIDに問題があります")
        print("\n考えられる原因:")
        print("   1. アプリケーションIDが無効")
        print("   2. アプリケーションが承認待ち状態")
        print("   3. アプリケーションURLが未設定または無効")
        print("   4. アカウントに問題がある")
        print("\n次のステップ:")
        print("   1. https://webservice.rakuten.co.jp/app/applications にアクセス")
        print("   2. アプリケーションのステータスを確認")
        print("   3. アプリケーションURLを実在するURLに設定")
        print("   4. 24時間待ってから再テスト")
        print("   5. それでも解決しない場合はサポートに問い合わせ")

    print("\n" + "="*60)
    print(f"チェックリストを確認: rakuten_api_checklist.md")
    print("="*60)

if __name__ == "__main__":
    main()
