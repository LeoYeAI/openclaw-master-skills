#!/usr/bin/env python3
"""
Bubble-O-Meter: 米国株式市場のバブル度を多面的に評価するスクリプト

8つの指標を0-2点で評価し、合計スコア(0-16点)でバブル度を判定:
- 0-4: 正常域
- 5-8: 警戒域
- 9-12: 熱狂域
- 13-16: 臨界域

使用方法:
    python bubble_scorer.py --ticker SPY --period 1y
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class BubbleScorer:
    """バブルスコアリングシステム"""
    
    def __init__(self):
        self.indicators = {
            "mass_penetration": {
                "name": "大衆浸透度",
                "weight": 2,
                "description": "非投資家層からの推奨・言及"
            },
            "media_saturation": {
                "name": "メディア飽和",
                "weight": 2,
                "description": "検索・SNS・メディア露出の急騰"
            },
            "new_accounts": {
                "name": "新規参入",
                "weight": 2,
                "description": "口座開設・資金流入の加速"
            },
            "new_issuance": {
                "name": "新規発行氾濫",
                "weight": 2,
                "description": "IPO/SPAC/関連商品の乱立"
            },
            "leverage": {
                "name": "レバレッジ",
                "weight": 2,
                "description": "証拠金・信用・資金調達レートの偏り"
            },
            "price_acceleration": {
                "name": "価格加速度",
                "weight": 2,
                "description": "リターンが歴史分布上位に到達"
            },
            "valuation_disconnect": {
                "name": "バリュエーション逸脱",
                "weight": 2,
                "description": "ファンダ説明が物語一辺倒に"
            },
            "breadth_expansion": {
                "name": "相関と幅",
                "weight": 2,
                "description": "低質銘柄まで全面高"
            }
        }
    
    def calculate_score(self, scores: Dict[str, int]) -> Dict:
        """
        各指標のスコアから総合評価を計算
        
        Args:
            scores: 各指標のスコア辞書 (0-2点)
        
        Returns:
            評価結果の辞書
        """
        total_score = sum(scores.values())
        max_score = len(self.indicators) * 2
        
        # バブル段階の判定
        if total_score <= 4:
            phase = "正常域"
            risk_level = "低"
            action = "通常通りの投資戦略を継続"
        elif total_score <= 8:
            phase = "警戒域"
            risk_level = "中"
            action = "部分利確の開始、新規ポジションのサイズ縮小"
        elif total_score <= 12:
            phase = "熱狂域"
            risk_level = "高"
            action = "階段状利確の加速、ATRトレーリングストップ厳格化、総リスク予算30-50%削減"
        else:
            phase = "臨界域"
            risk_level = "極めて高"
            action = "大幅な利確またはフルヘッジ、新規参入停止、反転確認後のショートポジション検討"
        
        # Minskyフェーズの推定
        minsky_phase = self._estimate_minsky_phase(scores, total_score)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(total_score / max_score * 100, 1),
            "phase": phase,
            "risk_level": risk_level,
            "minsky_phase": minsky_phase,
            "recommended_action": action,
            "indicator_scores": scores,
            "detailed_indicators": self._format_indicator_details(scores)
        }
    
    def _estimate_minsky_phase(self, scores: Dict[str, int], total: int) -> str:
        """Minsky/Kindlebergerフェーズの推定"""
        mass_pen = scores.get("mass_penetration", 0)
        media = scores.get("media_saturation", 0)
        price_acc = scores.get("price_acceleration", 0)
        
        if total <= 4:
            return "Displacement/Early Boom (きっかけ・初期拡張)"
        elif total <= 8:
            if media >= 1 and price_acc >= 1:
                return "Boom (拡張期)"
            else:
                return "Displacement/Early Boom (きっかけ・初期拡張)"
        elif total <= 12:
            if mass_pen >= 2 and media >= 2:
                return "Euphoria (熱狂期) - FOMOが制度化"
            else:
                return "Late Boom/Early Euphoria (拡張後期・熱狂初期)"
        else:
            if mass_pen >= 2:
                return "Peak Euphoria/Profit Taking (熱狂ピーク・利確開始) - 反転間近"
            else:
                return "Euphoria (熱狂期)"
    
    def _format_indicator_details(self, scores: Dict[str, int]) -> List[Dict]:
        """指標の詳細情報をフォーマット"""
        details = []
        for key, value in scores.items():
            indicator = self.indicators.get(key, {})
            status = "🔴高" if value == 2 else "🟡中" if value == 1 else "🟢低"
            details.append({
                "indicator": indicator.get("name", key),
                "score": value,
                "status": status,
                "description": indicator.get("description", "")
            })
        return details
    
    def get_scoring_guidelines(self) -> str:
        """各指標のスコアリングガイドラインを返す"""
        guidelines = """
## バブルスコアリング・ガイドライン

### 1. 大衆浸透度 (Mass Penetration)
- 0点: 専門家・投資家層のみの議論
- 1点: 一般層にも認知されるが、まだ投資対象としては限定的
- 2点: 非投資家（タクシー運転手、美容師、家族）が積極的に推奨・言及

### 2. メディア飽和 (Media Saturation)
- 0点: 通常レベルの報道・検索トレンド
- 1点: 検索トレンド、SNS言及が平常の2-3倍
- 2点: テレビ特集、雑誌表紙、検索トレンド急騰（平常の5倍以上）

### 3. 新規参入 (New Accounts & Inflows)
- 0点: 通常レベルの口座開設・入金
- 1点: 口座開設が前年比50-100%増
- 2点: 口座開設が前年比200%以上、「初めての投資」層の大量流入

### 4. 新規発行氾濫 (New Issuance Flood)
- 0点: 通常レベルのIPO/商品組成
- 1点: IPO/SPAC/関連ETFが前年比50%以上増加
- 2点: 低質なIPO乱立、「○○関連」ファンド・ETFの濫造

### 5. レバレッジ (Leverage Indicators)
- 0点: 証拠金残高・信用評価損益が正常範囲
- 1点: 証拠金残高が過去平均の1.5倍、先物ポジション偏り
- 2点: 証拠金残高が過去最高更新、資金調達レート高止まり、極端なポジション偏り

### 6. 価格加速度 (Price Acceleration)
- 0点: 年率リターンが歴史分布の中央値付近
- 1点: 年率リターンが過去90パーセンタイル超
- 2点: 年率リターンが過去95-99パーセンタイル、または加速度（2階微分）が正で増加

### 7. バリュエーション逸脱 (Valuation Disconnect)
- 0点: ファンダメンタルで合理的に説明可能
- 1点: 高バリュエーションだが「成長期待」で一応説明可能
- 2点: 説明が完全に「物語」「革命」「パラダイムシフト」に依存、「今回は違う」

### 8. 相関と幅 (Breadth & Correlation)
- 0点: 一部のリーダー銘柄のみ上昇
- 1点: セクター全体に波及、mid-capまで上昇
- 2点: 低質・low-cap銘柄まで全面高、「ゾンビ企業」も上昇（最後の買い手参入）
"""
        return guidelines
    
    def format_output(self, result: Dict) -> str:
        """結果を読みやすくフォーマット"""
        output = f"""
{'='*60}
🔍 米国市場バブル度評価 - Bubble-O-Meter
{'='*60}

評価日時: {result['timestamp']}

【総合スコア】
{result['total_score']}/{result['max_score']}点 ({result['percentage']}%)

【市場フェーズ】
現在: {result['phase']} (リスク: {result['risk_level']})
Minskyフェーズ: {result['minsky_phase']}

【推奨アクション】
{result['recommended_action']}

{'='*60}
【指標別スコア】
{'='*60}
"""
        for detail in result['detailed_indicators']:
            output += f"\n{detail['status']} {detail['indicator']}: {detail['score']}/2点\n"
            output += f"   └─ {detail['description']}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


def manual_assessment() -> Dict[str, int]:
    """対話型の手動評価"""
    scorer = BubbleScorer()
    print("\n" + "="*60)
    print("🔍 米国市場バブル度評価 - Manual Assessment")
    print("="*60)
    print("\n各指標を0-2点で評価してください:")
    print(scorer.get_scoring_guidelines())
    
    scores = {}
    for key, indicator in scorer.indicators.items():
        while True:
            try:
                score = int(input(f"\n{indicator['name']} (0-2): "))
                if 0 <= score <= 2:
                    scores[key] = score
                    break
                else:
                    print("0, 1, 2 のいずれかを入力してください")
            except ValueError:
                print("数値を入力してください")
    
    return scores


def main():
    parser = argparse.ArgumentParser(
        description="米国市場のバブル度を評価するBubble-O-Meter"
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="対話型の手動評価モード"
    )
    parser.add_argument(
        "--scores",
        type=str,
        help="JSON形式のスコア文字列 (例: '{\"mass_penetration\":2,\"media_saturation\":1,...}')"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="出力形式"
    )
    
    args = parser.parse_args()
    scorer = BubbleScorer()
    
    # スコアの取得
    if args.manual:
        scores = manual_assessment()
    elif args.scores:
        try:
            scores = json.loads(args.scores)
        except json.JSONDecodeError:
            print("エラー: 無効なJSON形式です")
            return 1
    else:
        print("エラー: --manual または --scores を指定してください")
        print("\nガイドラインを表示:")
        print(scorer.get_scoring_guidelines())
        return 1
    
    # 評価の実行
    result = scorer.calculate_score(scores)
    
    # 出力
    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(scorer.format_output(result))
    
    return 0


if __name__ == "__main__":
    exit(main())
