"""
导购个人业绩分析模块 - 增强版
支持 /api/v1/guide/detail 接口的丰富数据结构
"""

import sys
sys.path.insert(0, '/Users/yangguangwei/.openclaw/workspace-front-door')
from api_client import get_api_client
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any


def analyze(store_id: str, guide_name: str, 
            from_date: str, to_date: str,
            compare_with_store: bool = True):
    """
    分析单个导购的详细业绩表现
    
    Args:
        store_id: 门店ID
        guide_name: 导购姓名
        from_date: 分析开始日期 (YYYY-MM-DD)
        to_date: 分析结束日期 (YYYY-MM-DD)
        compare_with_store: 是否与门店平均对比
    
    Returns:
        dict: 分析结果
    """
    
    print(f"\n{'='*70}")
    print(f"导购个人业绩深度分析 - {guide_name}")
    print(f"分析周期: {from_date} 至 {to_date}")
    print(f"{'='*70}\n")
    
    # 【第一步：获取导购详细数据】
    print("【第一步：获取导购详细数据】")
    data = _get_guide_detail(store_id, guide_name, from_date, to_date)
    
    if not data:
        print("错误: 无法获取导购数据")
        return {"status": "error", "message": "无法获取导购数据"}
    
    overall = data.get('guideOverallPerformance', {})
    features = data.get('featureDistribution', {})
    sku_ranking = data.get('skuRanking', [])
    
    # 【第二步：获取订单分析数据】
    print("\n【第二步：获取订单分析数据】")
    order_data = _get_order_analysis(store_id, guide_name, from_date, to_date)
    
    # 【第三步：核心业绩指标分析】
    print("\n【第三步：核心业绩指标分析】")
    core_metrics = _analyze_core_metrics(overall)
    
    # 【第四步：雷达图能力对比】
    print("\n【第四步：雷达图能力对比】")
    radar_analysis = _analyze_radar(overall)
    
    # 【第五步：商品特征分析】
    print("\n【第五步：商品特征分析】")
    feature_analysis = _analyze_features(features)
    
    # 【第六步：爆品分析】
    print("\n【第六步：爆品分析】")
    sku_analysis = _analyze_sku_ranking(sku_ranking, from_date, to_date)
    
    # 【第七步：订单结构分析】
    print("\n【第七步：订单结构分析】")
    order_analysis = _analyze_order_structure(order_data)
    
    # 【第八步：AIoT客户漏斗分析】（仅AIoT门店）
    print("\n【第八步：AIoT客户漏斗分析】")
    funnel_analysis = _analyze_aiot_funnel(store_id, guide_name, from_date, to_date)
    
    # 【第九步：AIoT高试用低转化分析】（仅AIoT门店）
    print("\n【第九步：AIoT高试用低转化分析】")
    aiot_analysis = _analyze_aiot_conversion(store_id, guide_name, from_date, to_date, funnel_analysis)
    
    # 【第十步：销售额Top5与高试用低转化Top5对比】（仅AIoT门店且customer-funnel正常）
    print("\n【第十步：销售额Top5与高试用低转化Top5对比】")
    sku_trial_comparison = _analyze_sku_vs_trial(sku_analysis, aiot_analysis, funnel_analysis)
    
    # 【第十一步：14天趋势分析】
    print("\n【第十一步：14天趋势分析】")
    trend_analysis = _analyze_trend_14days(store_id, guide_name, from_date, to_date)
    
    # 【第十二步：综合诊断】
    print("\n【第十二步：综合诊断】")
    findings = _generate_findings(core_metrics, radar_analysis, feature_analysis, order_analysis, aiot_analysis, funnel_analysis, trend_analysis, sku_trial_comparison)
    recommendations = _generate_recommendations(findings, feature_analysis, order_analysis, aiot_analysis, funnel_analysis, trend_analysis, sku_trial_comparison)
    
    for finding in findings:
        emoji = "🔴" if finding['severity'] == 'high' else "🟡" if finding['severity'] == 'medium' else "🟢"
        print(f"  {emoji} [{finding['type']}] {finding['title']}")
    
    # 组装结果
    result = {
        "status": "ok",
        "store_id": store_id,
        "guide_name": guide_name,
        "analysis_period": {"from": from_date, "to": to_date},
        "core_metrics": core_metrics,
        "radar_analysis": radar_analysis,
        "feature_analysis": feature_analysis,
        "sku_analysis": sku_analysis,
        "order_analysis": order_analysis,
        "aiot_analysis": aiot_analysis,
        "funnel_analysis": funnel_analysis,
        "sku_trial_comparison": sku_trial_comparison,
        "trend_analysis": trend_analysis,
        "findings": findings,
        "recommendations": recommendations
    }
    
    print(f"\n{'='*70}")
    print("分析完成")
    print(f"{'='*70}\n")
    
    return result


def _get_guide_detail(store_id: str, guide_name: str, 
                      from_date: str, to_date: str) -> Dict:
    """获取导购详细数据"""
    try:
        client = get_api_client()
        params = {
            'guideName': guide_name,
            'storeId': store_id,
            'fromDate': from_date,
            'toDate': to_date
        }
        
        response = client.call_api('copilot', '/api/v1/guide/detail', params=params)
        return response
        
    except Exception as e:
        print(f"  错误: API获取失败 - {e}")
        return {}


def _get_order_analysis(store_id: str, guide_name: str,
                        from_date: str, to_date: str) -> Dict:
    """获取导购订单分析数据"""
    try:
        client = get_api_client()
        params = {
            'storeId': store_id,
            'fromDate': from_date,
            'toDate': to_date,
            'guideName': guide_name
        }
        
        response = client.call_api('copilot', '/api/v1/guide/order-analysis', params=params)
        return response
        
    except Exception as e:
        print(f"  警告: 订单分析API获取失败 - {e}")
        return {}


def _analyze_aiot_conversion(store_id: str, guide_name: str,
                             from_date: str, to_date: str,
                             funnel_analysis: Dict = None) -> Dict:
    """分析AIoT高试用低转化商品（仅AIoT门店）"""
    try:
        client = get_api_client()
        params = {
            'guideName': guide_name,
            'storeId': store_id,
            'fromDate': from_date,
            'toDate': to_date
        }

        response = client.call_api('copilot', '/api/v1/guide/high-trial-low-conversion', params=params)

        high_trial_items = response.get('highTrialLowConversion', [])

        if not high_trial_items:
            print("  无高试用低转化商品数据（可能为非AIoT门店）")
            return {'is_aiot_store': False, 'items': []}

        # 检查导购信息是否维护（funnel全为0时，high-trial-low-conversion返回的是门店整体数据）
        if funnel_analysis and funnel_analysis.get('is_aiot_store'):
            effective_customers = funnel_analysis.get('effective_customers', 0)
            deal_customers = funnel_analysis.get('deal_customers', 0)
            
            # 如果funnel数据全为0，说明导购信息未维护
            if effective_customers == 0 and deal_customers == 0:
                print(f"  ⚠️ 警告: 导购 '{guide_name}' 信息未在AIoT系统维护")
                print(f"  当前返回的是门店整体高试用低转化数据，非个人数据")
                return {
                    'is_aiot_store': True,
                    'guide_info_missing': True,
                    'note': f"导购 '{guide_name}' 信息未在AIoT系统维护，以下数据为门店整体数据",
                    'item_count': len(high_trial_items),
                    'total_trials': sum(item['trialCount'] for item in high_trial_items),
                    'items': []
                }

        # 分析高试用低转化商品
        analysis = {
            'is_aiot_store': True,
            'guide_info_missing': False,
            'item_count': len(high_trial_items),
            'total_trials': sum(item['trialCount'] for item in high_trial_items),
            'items': []
        }

        # 取前3个重点商品
        for item in high_trial_items[:3]:
            analysis['items'].append({
                'name': item.get('goodsName'),
                'code': item.get('goodsModelCode'),
                'trial_count': item.get('trialCount'),
                'deal_count': item.get('dealCount'),
                'conversion_rate': float(item.get('conversionRate', 0)),
                'price': item.get('standardPrice'),
                'image_url': item.get('imageUrl')
            })

        print(f"  发现 {analysis['item_count']} 个高试用低转化商品")
        print(f"  总试用次数: {analysis['total_trials']} 次")
        for item in analysis['items']:
            print(f"  - {item['name']}: 试用{item['trial_count']}次, 成交{item['deal_count']}件, 转化率{item['conversion_rate']:.0f}%")

        return analysis

    except Exception as e:
        print(f"  提示: AIoT转化分析API不可用（可能为非AIoT门店）- {e}")
        return {'is_aiot_store': False, 'items': []}


def _analyze_aiot_funnel(store_id: str, guide_name: str,
                         from_date: str, to_date: str) -> Dict:
    """分析AIoT客户漏斗（仅AIoT门店）"""
    try:
        client = get_api_client()
        params = {
            'guideName': guide_name,
            'storeId': store_id,
            'fromDate': from_date,
            'toDate': to_date
        }

        response = client.call_api('copilot', '/api/v1/guide/customer-funnel', params=params)

        funnel_data = response.get('customerFunnel', [])

        if not funnel_data:
            print("  无客户漏斗数据（可能为非AIoT门店）")
            return {'is_aiot_store': False, 'funnel': {}}

        # 解析漏斗数据
        funnel = {}
        for item in funnel_data:
            name = item.get('name')
            funnel[name] = {
                'value': item.get('value', 0),
                'percentage': float(item.get('percentage', 0)),
                'trend': item.get('trend', ''),
                'diff_value': item.get('diffValue', '0'),
                'link_relative_rate': float(item.get('linkRelativeRate', 0))
            }

        # 检查数据质量
        effective_customers = funnel.get('有效客户', {}).get('value', 0)
        deal_customers = funnel.get('成交客户', {}).get('value', 0)

        # 计算关键指标
        analysis = {
            'is_aiot_store': True,
            'funnel': funnel,
            'effective_customers': effective_customers,
            'deal_customers': deal_customers,
            'conversion_rate': round(deal_customers / effective_customers * 100, 1) if effective_customers > 0 else 0,
            'data_quality_issue': False
        }

        # 检查数据分层情况
        normal_customers = funnel.get('普通客户', {}).get('value', 0)
        potential_customers = funnel.get('潜在客户', {}).get('value', 0)
        intent_customers = funnel.get('意向客户', {}).get('value', 0)

        # 判断导购是否佩戴电子工牌
        if effective_customers > 0 and normal_customers == 0 and potential_customers == 0 and intent_customers == 0:
            analysis['badge_not_worn'] = True
            analysis['note'] = '导购未佩戴电子工牌，仅记录成交客户（通过订单系统），无法获取试用行为数据'
        else:
            analysis['badge_not_worn'] = False

        # 打印分析结果
        print(f"  有效客户: {analysis['effective_customers']}人")
        print(f"  成交客户: {analysis['deal_customers']}人")
        print(f"  成交转化率: {analysis['conversion_rate']:.1f}%")

        if analysis.get('badge_not_worn'):
            print(f"  ℹ️ 提示: {analysis['note']}")
        else:
            print(f"  普通客户: {normal_customers}人, 潜在客户: {potential_customers}人, 意向客户: {intent_customers}人")

        # 打印环比变化
        if funnel.get('有效客户', {}).get('trend'):
            trend_symbol = "↓" if funnel['有效客户']['trend'] == 'down' else "↑" if funnel['有效客户']['trend'] == 'up' else "→"
            print(f"  有效客户环比: {trend_symbol} {funnel['有效客户']['link_relative_rate']:.1f}%")

        return analysis

    except Exception as e:
        print(f"  提示: AIoT客户漏斗API不可用（可能为非AIoT门店）- {e}")
        return {'is_aiot_store': False, 'funnel': {}}


def _analyze_core_metrics(overall: Dict) -> Dict:
    """分析核心业绩指标"""
    metrics = {}
    
    # 基础指标
    metrics['sales'] = {
        'amount': round(overall.get('salesAmount', 0), 2),
        'rank': overall.get('salesAmountRank', 0),
        'share': round(overall.get('performanceShare', 0), 2)
    }
    
    metrics['orders'] = {
        'count': overall.get('effectiveOrderCount', 0),
        'rank': overall.get('effectiveOrderCountRank', 0)
    }
    
    metrics['atv'] = {
        'value': round(overall.get('customerUnitPrice', 0), 2),
        'rank': overall.get('customerUnitPriceRank', 0)
    }
    
    metrics['attach'] = {
        'qty_ratio': round(overall.get('attachQtyRatio', 0), 2),
        'sku_ratio': round(overall.get('attachSkuRatio', 0), 2)
    }
    
    metrics['new_customers'] = {
        'count': overall.get('newCustomerCount', 0),
        'rank': overall.get('newCustomerCountRank', 0)
    }
    
    metrics['efficiency'] = {
        'value': round(overall.get('guideEfficiencyValue', 0), 2),
        'rank': overall.get('guideEfficiencyValueRank', 0),
        'order_days': overall.get('orderDaysCount', 0)
    }
    
    # 打印核心指标
    print(f"  销售额: ¥{metrics['sales']['amount']:,.0f} (排名#{metrics['sales']['rank']}, 占比{metrics['sales']['share']:.1f}%)")
    print(f"  订单数: {metrics['orders']['count']}单 (排名#{metrics['orders']['rank']})")
    print(f"  客单价: ¥{metrics['atv']['value']:.0f} (排名#{metrics['atv']['rank']})")
    print(f"  连带率: {metrics['attach']['qty_ratio']:.2f}")
    print(f"  新客数: {metrics['new_customers']['count']}人 (排名#{metrics['new_customers']['rank']})")
    print(f"  人效值: {metrics['efficiency']['value']:.0f} (排名#{metrics['efficiency']['rank']})")
    print(f"  有订单天数: {metrics['efficiency']['order_days']}天")
    
    return metrics


def _analyze_radar(overall: Dict) -> Dict:
    """分析雷达图能力对比"""
    guide_radar = overall.get('guideRadarReference', {})
    store_radar = overall.get('storeRadarReference', {})
    
    if not guide_radar or not store_radar:
        return {}
    
    # 6维能力对比
    dimensions = ['salesAmount', 'effectiveOrderCount', 'newCustomerCount', 
                  'customerUnitPrice', 'qtyUnitPrice', 'attachQtyRatio']
    
    comparison = {}
    for dim in dimensions:
        guide_val = guide_radar.get(dim, 0)
        store_val = store_radar.get(dim, 0)
        
        if store_val > 0:
            ratio = guide_val / store_val
        else:
            ratio = 1.0 if guide_val > 0 else 0
        
        comparison[dim] = {
            'guide': guide_val,
            'store_avg': store_val,
            'ratio': round(ratio, 2),
            'gap': round(guide_val - store_val, 2)
        }
    
    # 打印雷达对比
    print(f"  销售额: 导购¥{comparison['salesAmount']['guide']:.0f} vs 门店平均¥{comparison['salesAmount']['store_avg']:.0f} ({comparison['salesAmount']['ratio']*100:.0f}%)")
    print(f"  订单数: 导购{comparison['effectiveOrderCount']['guide']:.0f} vs 门店平均{comparison['effectiveOrderCount']['store_avg']:.0f} ({comparison['effectiveOrderCount']['ratio']*100:.0f}%)")
    print(f"  新客数: 导购{comparison['newCustomerCount']['guide']:.0f} vs 门店平均{comparison['newCustomerCount']['store_avg']:.0f} ({comparison['newCustomerCount']['ratio']*100:.0f}%)")
    print(f"  客单价: 导购¥{comparison['customerUnitPrice']['guide']:.0f} vs 门店平均¥{comparison['customerUnitPrice']['store_avg']:.0f} ({comparison['customerUnitPrice']['ratio']*100:.0f}%)")
    print(f"  件单价: 导购¥{comparison['qtyUnitPrice']['guide']:.0f} vs 门店平均¥{comparison['qtyUnitPrice']['store_avg']:.0f} ({comparison['qtyUnitPrice']['ratio']*100:.0f}%)")
    print(f"  连带率: 导购{comparison['attachQtyRatio']['guide']:.2f} vs 门店平均{comparison['attachQtyRatio']['store_avg']:.2f} ({comparison['attachQtyRatio']['ratio']*100:.0f}%)")
    
    return comparison


def _analyze_features(features: Dict) -> Dict:
    """分析商品特征分布"""
    analysis = {}
    
    # 品类分析
    category = features.get('categoryFeature', [])
    if category:
        analysis['category'] = {
            'top': category[0]['name'],
            'top_percentage': int(category[0]['moneyPercentage']),
            'distribution': [(c['name'], int(c['moneyPercentage'])) for c in category[:5]]
        }
        print(f"  主营品类: {analysis['category']['top']} ({analysis['category']['top_percentage']}%)")
    
    # 价格带分析
    price_range = features.get('priceRangeFeature', [])
    if price_range:
        # 计算高客单占比（800元以上）
        def parse_price_range(name):
            """解析价格带名称，返回起始价格"""
            if '以下' in name:
                return 0
            elif '以上' in name:
                return int(name.replace('以上', ''))
            else:
                return int(name.split('-')[0])
        
        high_price_items = [p for p in price_range if parse_price_range(p['name']) >= 800]
        high_price_pct = sum(int(p['moneyPercentage']) for p in high_price_items)
        
        analysis['price_range'] = {
            'top': price_range[0]['name'],
            'top_percentage': int(price_range[0]['moneyPercentage']),
            'high_price_ratio': high_price_pct,
            'distribution': [(p['name'], int(p['moneyPercentage'])) for p in price_range[:5]]
        }
        print(f"  主销价格带: {analysis['price_range']['top']}元 ({analysis['price_range']['top_percentage']}%)")
        print(f"  高客单占比(≥800元): {high_price_pct}%")
    
    # 包型分析
    shape = features.get('shapeFeature', [])
    if shape:
        analysis['shape'] = {
            'top': shape[0]['name'],
            'top_percentage': int(shape[0]['moneyPercentage']),
            'distribution': [(s['name'], int(s['moneyPercentage'])) for s in shape[:5]]
        }
        print(f"  主销包型: {analysis['shape']['top']} ({analysis['shape']['top_percentage']}%)")
    
    # 颜色分析
    color = features.get('colorFeature', [])
    if color:
        analysis['color'] = {
            'top': color[0]['name'],
            'top_percentage': int(color[0]['moneyPercentage'])
        }
        print(f"  主销颜色: {analysis['color']['top']} ({analysis['color']['top_percentage']}%)")
    
    # 新品分析（2026年上市）
    launch_date = features.get('launchDateFeature', [])
    if launch_date:
        new_items = [l for l in launch_date if '2026' in l['name']]
        new_item_pct = sum(int(l['moneyPercentage']) for l in new_items)
        analysis['new_items'] = {
            'ratio': new_item_pct,
            'top_new': new_items[0]['name'] if new_items else None
        }
        print(f"  新品销售占比(2026年): {new_item_pct}%")
    
    return analysis


def _analyze_sku_ranking(sku_ranking: List, from_date: str = None, to_date: str = None) -> Dict:
    """分析爆品表现 - Top5 SKU（含SPU集中度、上市时间、新品识别）"""
    if not sku_ranking:
        return {}
    
    # 分析Top5 SKU
    analysis = {
        'top5_skus': [],
        'total_skus': len(sku_ranking),
        'top5_total_sales': 0,
        'top5_total_qty': 0,
        'spu_concentration': {},
        'launch_date_analysis': {},
        'new_items': []
    }
    
    # 解析分析周期（用于判断新品）
    analysis_year = None
    analysis_month = None
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            analysis_year = from_dt.year
            analysis_month = from_dt.month
        except:
            pass
    
    # SPU统计（按商品名称聚合）
    spu_stats = {}
    launch_dates = []
    
    # 取前5个SKU
    for i, sku in enumerate(sku_ranking[:5], 1):
        # 解析上市日期
        launch_date_str = sku.get('goodsLauchDate', '')
        launch_year = None
        launch_month = None
        is_new = False
        months_diff = None
        
        if launch_date_str:
            try:
                # 格式: "2025/7/1"
                parts = launch_date_str.split('/')
                if len(parts) >= 2:
                    launch_year = int(parts[0])
                    launch_month = int(parts[1])
                    
                    # 判断是否为新品（成交时月份 - 上市月份 ≤ 3）
                    if analysis_year and analysis_month and launch_year and launch_month:
                        months_diff = (analysis_year - launch_year) * 12 + (analysis_month - launch_month)
                        is_new = months_diff <= 3  # 可以为负值（预售）
                        launch_dates.append({
                            'year': launch_year,
                            'month': launch_month,
                            'months_diff': months_diff,
                            'is_new': is_new,
                            'name': sku.get('goodsName')
                        })
            except:
                pass
        
        sku_data = {
            'rank': i,
            'name': sku.get('goodsName'),
            'code': sku.get('goodsModelCode'),
            'sales': round(sku.get('dealAmount', 0), 2),
            'qty': sku.get('qty', 0),
            'avg_price': round(sku.get('dealAvgAmount', 0), 2),
            'contribute_rate': round(sku.get('contributeRate', 0), 2),
            'standard_price': sku.get('standardPrice', 0),
            'launch_date': launch_date_str,
            'launch_year': launch_year,
            'launch_month': launch_month,
            'is_new': is_new,
            'months_diff': months_diff,
            'image_url': sku.get('imageUrl')
        }
        analysis['top5_skus'].append(sku_data)
        analysis['top5_total_sales'] += sku_data['sales']
        analysis['top5_total_qty'] += sku_data['qty']
        
        # SPU统计
        spu_name = sku.get('goodsName', '')
        if spu_name not in spu_stats:
            spu_stats[spu_name] = {'count': 0, 'sales': 0, 'qty': 0}
        spu_stats[spu_name]['count'] += 1
        spu_stats[spu_name]['sales'] += sku_data['sales']
        spu_stats[spu_name]['qty'] += sku_data['qty']
        
        # 记录新品
        if is_new:
            analysis['new_items'].append(sku_data)
    
    # SPU集中度分析
    analysis['spu_concentration'] = {
        'total_spu': len(spu_stats),
        'spu_list': sorted([
            {'name': name, 'sku_count': stats['count'], 'sales': stats['sales'], 'qty': stats['qty']}
            for name, stats in spu_stats.items()
        ], key=lambda x: x['sales'], reverse=True)
    }
    
    # 上市时间偏好分析
    if launch_dates:
        new_items_count = sum(1 for d in launch_dates if d['is_new'])
        analysis['launch_date_analysis'] = {
            'total_items': len(launch_dates),
            'new_items_count': new_items_count,
            'new_items_ratio': round(new_items_count / len(launch_dates) * 100, 1),
            'launch_dates': launch_dates
        }
    
    # 打印Top5列表
    print(f"  Top5 SKU 列表（共{analysis['total_skus']}个SKU）:")
    print(f"  {'排名':<4} {'款号':<12} {'名称':<10} {'销量':>4} {'销售额':>10} {'均价':>8} {'门店贡献':>8} {'上市时间':>10} {'新品':>4}")
    print(f"  {'-'*85}")
    for sku in analysis['top5_skus']:
        new_flag = "✓" if sku['is_new'] else ""
        launch_str = f"{sku['launch_year']}/{sku['launch_month']}" if sku['launch_year'] else "-"
        print(f"  #{sku['rank']:<3} {sku['code']:<12} {sku['name']:<10} {sku['qty']:>4}件 ¥{sku['sales']:>8,.0f} ¥{sku['avg_price']:>6,.0f} {sku['contribute_rate']:>7.0f}% {launch_str:>10} {new_flag:>4}")
    
    print(f"  {'-'*85}")
    print(f"  Top5合计: 销量{analysis['top5_total_qty']}件, 销售额¥{analysis['top5_total_sales']:,.0f}")
    print(f"  注: 门店贡献率 = 导购该SKU销售额 / 门店该SKU总销售额")
    
    # 打印SPU集中度
    print(f"\n  SPU集中度分析:")
    print(f"  共涉及{analysis['spu_concentration']['total_spu']}个SPU（商品名称）")
    for spu in analysis['spu_concentration']['spu_list']:
        print(f"  - {spu['name']}: {spu['sku_count']}个SKU, 销量{spu['qty']}件, 销售额¥{spu['sales']:,.0f}")
    
    # 打印上市时间偏好
    if analysis['launch_date_analysis']:
        la = analysis['launch_date_analysis']
        print(f"\n  上市时间偏好:")
        print(f"  新品占比: {la['new_items_count']}/{la['total_items']} ({la['new_items_ratio']}%)")
        if la['new_items_count'] > 0:
            print(f"  新品列表:")
            for item in analysis['new_items']:
                diff_str = f"{item['months_diff']:+.0f}月" if item['months_diff'] is not None else ""
                print(f"  - {item['name']} ({item['code']}): {item['launch_date']} {diff_str}")
    
    return analysis


def _analyze_sku_vs_trial(sku_analysis: Dict, aiot_analysis: Dict, funnel_analysis: Dict = None) -> Dict:
    """分析销售额Top5与高试用低转化Top5的对比"""
    if not sku_analysis or not aiot_analysis or not aiot_analysis.get('is_aiot_store'):
        return {}
    
    # 如果导购信息未维护，跳过对比
    if aiot_analysis.get('guide_info_missing'):
        return {'can_compare': False, 'reason': '导购AIoT信息未维护'}
    
    # 如果customer-funnel数据异常（全为0），跳过对比
    if funnel_analysis and funnel_analysis.get('is_aiot_store'):
        effective_customers = funnel_analysis.get('effective_customers', 0)
        deal_customers = funnel_analysis.get('deal_customers', 0)
        if effective_customers == 0 and deal_customers == 0:
            return {'can_compare': False, 'reason': 'customer-funnel数据异常（全为0）'}
    
    analysis = {
        'can_compare': True,
        'sales_top5_codes': set(),
        'trial_top5_codes': set(),
        'overlap': [],  # 同时在两个列表中的商品
        'sales_only': [],  # 只在销售额Top5中
        'trial_only': [],  # 只在试用低转化Top5中
        'new_item_in_trial': []  # 高试用低转化中的新品
    }
    
    # 获取销售额Top5的款号
    for sku in sku_analysis.get('top5_skus', []):
        analysis['sales_top5_codes'].add(sku['code'])
    
    # 获取高试用低转化Top5的款号
    for item in aiot_analysis.get('items', []):
        analysis['trial_top5_codes'].add(item['code'])
    
    # 找出重叠商品
    overlap_codes = analysis['sales_top5_codes'] & analysis['trial_top5_codes']
    
    # 分析重叠商品
    for code in overlap_codes:
        sku_info = next((s for s in sku_analysis['top5_skus'] if s['code'] == code), None)
        trial_info = next((i for i in aiot_analysis['items'] if i['code'] == code), None)
        if sku_info and trial_info:
            analysis['overlap'].append({
                'code': code,
                'name': sku_info['name'],
                'sales': sku_info['sales'],
                'trial_count': trial_info['trial_count'],
                'is_new': sku_info.get('is_new', False)
            })
    
    # 只在销售额Top5中的商品
    for sku in sku_analysis.get('top5_skus', []):
        if sku['code'] not in overlap_codes:
            analysis['sales_only'].append({
                'code': sku['code'],
                'name': sku['name'],
                'sales': sku['sales'],
                'is_new': sku.get('is_new', False)
            })
    
    # 只在试用低转化Top5中的商品
    for item in aiot_analysis.get('items', []):
        if item['code'] not in overlap_codes:
            analysis['trial_only'].append({
                'code': item['code'],
                'name': item['name'],
                'trial_count': item['trial_count'],
                'is_new': item.get('is_new', False)
            })
            if item.get('is_new'):
                analysis['new_item_in_trial'].append(item)
    
    # 打印对比分析
    print(f"\n  销售额Top5 vs 高试用低转化Top5 对比分析:")
    print(f"  {'='*60}")
    
    if analysis['overlap']:
        print(f"\n  🔶 重叠商品（高试用且高销售）:")
        for item in analysis['overlap']:
            new_flag = " [新品]" if item['is_new'] else ""
            print(f"    - {item['name']} ({item['code']}): 销售¥{item['sales']:,.0f}, 试用{item['trial_count']}次{new_flag}")
    
    if analysis['sales_only']:
        print(f"\n  ✅ 仅销售额Top5（销售好但试用少）:")
        for item in analysis['sales_only']:
            new_flag = " [新品]" if item['is_new'] else ""
            print(f"    - {item['name']} ({item['code']}): 销售¥{item['sales']:,.0f}{new_flag}")
    
    if analysis['trial_only']:
        print(f"\n  ⚠️ 仅高试用低转化Top5（试用多但未成交）:")
        for item in analysis['trial_only']:
            new_flag = " [新品]" if item['is_new'] else ""
            print(f"    - {item['name']} ({item['code']}): 试用{item['trial_count']}次{new_flag}")
    
    # 新品转化问题分析
    if analysis['new_item_in_trial']:
        print(f"\n  📌 新品转化问题:")
        print(f"    高试用低转化商品中有 {len(analysis['new_item_in_trial'])} 个新品:")
        for item in analysis['new_item_in_trial']:
            print(f"    - {item['name']} ({item['code']}): 试用{item['trial_count']}次，成交{item.get('deal_count', 0)}件")
        print(f"    建议: 加强新品卖点培训和试用后跟进转化")
    
    # SPU集中度对比
    sales_spu = set(s['name'] for s in sku_analysis.get('top5_skus', []))
    trial_spu = set(i['name'] for i in aiot_analysis.get('items', []))
    all_spu = sales_spu | trial_spu
    
    print(f"\n  📊 SPU集中度分析:")
    print(f"    销售额Top5涉及SPU: {len(sales_spu)}个")
    print(f"    高试用低转化Top5涉及SPU: {len(trial_spu)}个")
    print(f"    合计涉及SPU: {len(all_spu)}个")
    
    overlap_spu = sales_spu & trial_spu
    if overlap_spu:
        print(f"    重叠SPU: {', '.join(overlap_spu)}")
    
    return analysis


def _analyze_order_structure(order_data: Dict) -> Dict:
    """分析订单结构"""
    if not order_data:
        return {}
    
    analysis = {}
    
    # 1. 折扣分析
    discounts = order_data.get('OrderDiscounts', {})
    if discounts:
        discount_list = discounts.get('list', [])
        # 找到占比最高的折扣区间
        main_discount = max(discount_list, key=lambda x: x['dealShare']) if discount_list else None
        
        # 计算高折扣订单占比（6折以下）
        def is_low_discount(name):
            """判断是否为低折扣（6折以下）"""
            if '以下' in name:
                # 提取数字，如"6折以下" -> 6
                import re
                match = re.search(r'(\d+)', name)
                if match:
                    return int(match.group(1)) <= 6
            elif '-' in name:
                # 如"8-9折"，取第一个数字
                parts = name.split('-')
                try:
                    return float(parts[0]) < 6
                except:
                    return False
            elif '以上' in name:
                # 9折以上不算低折扣
                return False
            return False
        
        low_discount_items = [d for d in discount_list if is_low_discount(d['name'])]
        low_discount_pct = sum(d['orderCountShare'] for d in low_discount_items) * 100
        
        analysis['discount'] = {
            'main_range': main_discount['name'] if main_discount else None,
            'main_share': round(main_discount['dealShare'] * 100, 1) if main_discount else 0,
            'low_discount_ratio': round(low_discount_pct, 1),
            'total_orders': discounts.get('effectiveOrderCount', 0),
            'distribution': [(d['name'], round(d['dealShare'] * 100, 1)) for d in discount_list]
        }
        print(f"  主销折扣区间: {analysis['discount']['main_range']} ({analysis['discount']['main_share']}%)")
        print(f"  低折扣订单占比(6折以下): {analysis['discount']['low_discount_ratio']}%")
    
    # 2. 连带分析
    attachs = order_data.get('OrderAttachs', {})
    if attachs:
        attach_list = attachs.get('list', [])
        # 计算1件单占比
        single_item = next((a for a in attach_list if a['name'] == '1件单'), None)
        single_item_pct = single_item['orderCountShare'] * 100 if single_item else 0
        
        # 计算多连带订单占比（3件及以上）
        multi_items = [a for a in attach_list if '3件' in a['name'] or '4件' in a['name'] or '及以上' in a['name']]
        multi_item_pct = sum(a['orderCountShare'] for a in multi_items) * 100
        
        analysis['attach'] = {
            'single_item_ratio': round(single_item_pct, 1),
            'multi_item_ratio': round(multi_item_pct, 1),
            'avg_attach': round(attachs.get('dealQty', 0) / attachs.get('effectiveOrderCount', 1), 2) if attachs.get('effectiveOrderCount') else 0,
            'total_orders': attachs.get('effectiveOrderCount', 0),
            'distribution': [(a['name'], round(a['orderCountShare'] * 100, 1)) for a in attach_list]
        }
        print(f"  1件单占比: {analysis['attach']['single_item_ratio']}%")
        print(f"  多连带占比(≥3件): {analysis['attach']['multi_item_ratio']}%")
        print(f"  平均连带: {analysis['attach']['avg_attach']:.2f}")
    
    # 3. 会员分析
    members = order_data.get('OrderMembers', {})
    if members:
        member_list = members.get('list', [])
        old_member = next((m for m in member_list if m['name'] == '老会员'), None)
        new_member = next((m for m in member_list if m['name'] == '新会员'), None)
        non_member = next((m for m in member_list if m['name'] == '非会员'), None)
        
        analysis['member'] = {
            'old_member_ratio': round(old_member['dealShare'] * 100, 1) if old_member else 0,
            'new_member_ratio': round(new_member['dealShare'] * 100, 1) if new_member else 0,
            'non_member_ratio': round(non_member['dealShare'] * 100, 1) if non_member else 0,
            'total_customers': members.get('memberCount', 0),
            'distribution': [(m['name'], round(m['dealShare'] * 100, 1)) for m in member_list]
        }
        print(f"  老会员占比: {analysis['member']['old_member_ratio']}%")
        print(f"  新会员占比: {analysis['member']['new_member_ratio']}%")
        print(f"  非会员占比: {analysis['member']['non_member_ratio']}%")
    
    return analysis


def _generate_findings(core: Dict, radar: Dict, features: Dict, order: Dict = None, aiot: Dict = None, funnel: Dict = None, trend: Dict = None, sku_trial: Dict = None) -> List:
    """生成诊断发现"""
    findings = []

    # 1. 业绩排名分析
    if core['sales']['rank'] == 1:
        findings.append({
            'title': '业绩排名门店第一',
            'type': 'strength',
            'severity': 'low',
            'metric': 'sales_rank',
            'evidence': f"销售额排名#{core['sales']['rank']}, 业绩占比{core['sales']['share']:.1f}%",
            'implication': '该导购是门店业绩支柱'
        })
    elif core['sales']['rank'] <= 3:
        findings.append({
            'title': '业绩表现良好',
            'type': 'strength',
            'severity': 'low',
            'metric': 'sales_rank',
            'evidence': f"销售额排名#{core['sales']['rank']}",
            'implication': '处于团队中上游水平'
        })
    else:
        findings.append({
            'title': '业绩排名靠后',
            'type': 'weakness',
            'severity': 'medium',
            'metric': 'sales_rank',
            'evidence': f"销售额排名#{core['sales']['rank']}",
            'implication': '有较大的提升空间'
        })

    # 2. 雷达图能力分析
    if radar:
        # 新客获取能力
        if radar['newCustomerCount']['ratio'] > 1.5:
            findings.append({
                'title': '新客获取能力突出',
                'type': 'strength',
                'severity': 'low',
                'metric': 'new_customer',
                'evidence': f"新客数是门店平均的{radar['newCustomerCount']['ratio']*100:.0f}%",
                'implication': '客户开发能力强，可作为团队标杆'
            })
        elif radar['newCustomerCount']['ratio'] < 0.7:
            findings.append({
                'title': '新客获取能力不足',
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'new_customer',
                'evidence': f"新客数仅为门店平均的{radar['newCustomerCount']['ratio']*100:.0f}%",
                'implication': '需要加强客户开发和引流能力'
            })

        # 客单价能力
        if radar['customerUnitPrice']['ratio'] < 0.85:
            findings.append({
                'title': '客单价低于门店平均',
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'atv',
                'evidence': f"客单价为门店平均的{radar['customerUnitPrice']['ratio']*100:.0f}%",
                'implication': '连带销售或高价值商品推荐能力不足'
            })

    # 3. 品类集中度分析
    if features.get('category') and features['category']['top_percentage'] > 70:
        findings.append({
            'title': '品类销售过于集中',
            'type': 'risk',
            'severity': 'medium',
            'metric': 'category_concentration',
            'evidence': f"{features['category']['top']}占比{features['category']['top_percentage']}%",
            'implication': '过度依赖单一品类，抗风险能力弱'
        })

    # 4. 价格带分析
    if features.get('price_range') and features['price_range']['high_price_ratio'] < 30:
        findings.append({
            'title': '高客单销售能力弱',
            'type': 'weakness',
            'severity': 'medium',
            'metric': 'high_price_ratio',
            'evidence': f"800元以上商品销售占比仅{features['price_range']['high_price_ratio']}%",
            'implication': '需要提升高价值商品销售技巧'
        })

    # 5. 订单结构分析
    if order:
        # 连带分析
        if order.get('attach') and order['attach']['single_item_ratio'] > 60:
            findings.append({
                'title': '连带销售能力不足',
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'single_item_ratio',
                'evidence': f"1件单占比高达{order['attach']['single_item_ratio']}%",
                'implication': '连带销售技巧有待提升，错失升单机会'
            })

        # 低折扣订单分析
        if order.get('discount') and order['discount']['low_discount_ratio'] > 20:
            findings.append({
                'title': '低折扣订单占比过高',
                'type': 'risk',
                'severity': 'medium',
                'metric': 'low_discount_ratio',
                'evidence': f"6折以下订单占比{order['discount']['low_discount_ratio']}%",
                'implication': '可能存在过度依赖特价商品或议价能力弱的问题'
            })

    # 6. AIoT高试用低转化分析（仅AIoT门店）
    if aiot and aiot.get('is_aiot_store'):
        # 导购信息未维护
        if aiot.get('guide_info_missing'):
            findings.append({
                'title': f"导购 '{guide_name}' AIoT信息未维护",
                'type': 'risk',
                'severity': 'medium',
                'metric': 'aiot_guide_info_missing',
                'evidence': "客户漏斗数据全为0，高试用低转化数据为门店整体数据",
                'implication': '请在AIoT系统中维护导购信息，以获取个人准确的试用转化数据'
            })
        elif aiot.get('item_count', 0) >= 3:
            findings.append({
                'title': f"存在{aiot['item_count']}个高试用低转化商品",
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'high_trial_low_conversion',
                'evidence': f"{aiot['items'][0]['name']}等商品试用{aiot['items'][0]['trial_count']}次但0成交",
                'implication': '客户有试用意愿但导购跟进转化不到位，需加强试用后跟进'
            })

    # 7. AIoT客户漏斗分析（仅AIoT门店）
    if funnel and funnel.get('is_aiot_store'):
        # 检查导购是否佩戴电子工牌
        if funnel.get('badge_not_worn'):
            # 未佩戴工牌，只记录成交客户，这是正常情况
            pass  # 不生成异常诊断
        else:
            # 佩戴了工牌，可以正常分析试用行为数据
            # 这里可以添加基于试用行为的诊断
            pass

        # 有效客户环比下降（无论是否佩戴工牌都需要关注）
        if funnel.get('funnel', {}).get('有效客户', {}).get('trend') == 'down':
            decline_rate = funnel['funnel']['有效客户'].get('link_relative_rate', 0)
            if decline_rate > 20:
                findings.append({
                    'title': f'有效客户环比下降{decline_rate:.0f}%',
                    'type': 'weakness',
                    'severity': 'high',
                    'metric': 'effective_customer_decline',
                    'evidence': f"本期有效客户{funnel['effective_customers']}人，环比下降{decline_rate:.0f}%",
                    'implication': '进店客流或客户互动量显著下降，需关注引流和邀约'
                })

    # 8. 14天趋势分析
    if trend and trend.get('has_data'):
        # 无销售天数过多
        if trend['zero_days'] >= 5:
            findings.append({
                'title': f'近14天有{trend["zero_days"]}天无销售',
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'zero_sales_days',
                'evidence': f"14天中{trend['zero_days']}天销售额为0，占比{round(trend['zero_days']/trend['total_days']*100)}%",
                'implication': '销售连续性差，存在明显的销售空档'
            })
        
        # 日均销售额过低（低于平均值的50%）
        if trend['avg_daily_sales'] < 1000:
            findings.append({
                'title': f'日均销售额偏低',
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'low_daily_sales',
                'evidence': f"近14天日均销售额¥{trend['avg_daily_sales']:,.0f}",
                'implication': '日常销售产出不足，需要提升日均成交单量或客单价'
            })

    # 9. 销售额Top5与高试用低转化Top5对比分析（仅AIoT门店）
    if sku_trial and sku_trial.get('can_compare'):
        # 新品在高试用低转化中占比高
        if sku_trial.get('new_item_in_trial') and len(sku_trial['new_item_in_trial']) >= 2:
            findings.append({
                'title': f"高试用低转化商品中新品占比高",
                'type': 'weakness',
                'severity': 'medium',
                'metric': 'new_item_trial_no_conversion',
                'evidence': f"{len(sku_trial['new_item_in_trial'])}个新品试用多但未成交",
                'implication': '新品卖点讲解或试用后跟进转化存在问题'
            })
        
        # 销售额Top5与高试用低转化无重叠（说明销售好的商品试用少）
        if not sku_trial.get('overlap') and sku_trial.get('sales_only') and sku_trial.get('trial_only'):
            findings.append({
                'title': "销售额Top5与高试用低转化Top5无重叠",
                'type': 'hypothesis',
                'severity': 'low',
                'metric': 'sales_trial_mismatch',
                'evidence': "销售好的商品试用少，试用多的商品未成交",
                'implication': '需要分析是商品本身问题还是跟进转化问题'
            })

    return findings


def _generate_recommendations(findings: List, features: Dict, order: Dict = None, aiot: Dict = None, funnel: Dict = None, trend: Dict = None, sku_trial: Dict = None) -> List:
    """生成行动建议"""
    recommendations = []

    for finding in findings:
        if finding['type'] == 'weakness':
            if finding['metric'] == 'new_customer':
                recommendations.append({
                    'priority': 'high',
                    'action': '新客开发培训',
                    'details': '学习客户引流技巧、会员招募话术、社群运营方法',
                    'expected_impact': '新客数提升至门店平均水平'
                })
            elif finding['metric'] == 'atv':
                recommendations.append({
                    'priority': 'high',
                    'action': '客单价提升训练',
                    'details': '学习连带销售技巧、高价值商品卖点、场景化推荐',
                    'expected_impact': '客单价提升15-20%'
                })
            elif finding['metric'] == 'high_price_ratio':
                recommendations.append({
                    'priority': 'medium',
                    'action': '高客单商品专项培训',
                    'details': f"重点学习{features.get('price_range', {}).get('distribution', [['1000-1200', 0]])[0][0]}价格带商品卖点",
                    'expected_impact': '高客单占比提升至40%以上'
                })
            elif finding['metric'] == 'single_item_ratio':
                recommendations.append({
                    'priority': 'high',
                    'action': '连带销售强化训练',
                    'details': '练习二拍一话术、搭配推荐技巧、场景化连带销售',
                    'expected_impact': '1件单占比降至50%以下，连带率提升0.3-0.5'
                })
            elif finding['metric'] == 'high_trial_low_conversion':
                # AIoT专属建议
                top_item = aiot['items'][0] if aiot and aiot.get('items') else None
                item_name = top_item['name'] if top_item else '高试用商品'
                recommendations.append({
                    'priority': 'high',
                    'action': '试用跟进转化专项',
                    'details': f"针对{item_name}等试用未成交商品，学习试用后跟进话术、异议处理、促单技巧",
                    'expected_impact': '高试用商品转化率提升至30%以上'
                })
            elif finding['metric'] == 'aiot_guide_info_missing':
                recommendations.append({
                    'priority': 'high',
                    'action': '维护AIoT导购信息',
                    'details': '联系门店管理员在AIoT系统中维护该导购的工牌绑定和信息录入',
                    'expected_impact': '获取准确的个人试用转化数据'
                })
            elif finding['metric'] == 'effective_customer_decline':
                recommendations.append({
                    'priority': 'high',
                    'action': '客流提升专项',
                    'details': '加强邀约回店、社群运营、老客带新等引流措施',
                    'expected_impact': '有效客户数恢复至上期水平'
                })
            elif finding['metric'] == 'zero_sales_days':
                recommendations.append({
                    'priority': 'medium',
                    'action': '销售连续性提升',
                    'details': '制定每日销售目标，加强客户跟进，减少无销售天数',
                    'expected_impact': '无销售天数减少至3天以下'
                })
            elif finding['metric'] == 'low_daily_sales':
                recommendations.append({
                    'priority': 'medium',
                    'action': '日均产出提升',
                    'details': '提升日均订单数或客单价，确保每天都有成交',
                    'expected_impact': '日均销售额提升至¥1000以上'
                })
            elif finding['metric'] == 'new_item_trial_no_conversion':
                recommendations.append({
                    'priority': 'high',
                    'action': '新品转化专项提升',
                    'details': '加强新品卖点培训，优化试用体验，强化试用后跟进转化话术',
                    'expected_impact': '新品试用转化率提升至30%以上'
                })

        elif finding['type'] == 'risk':
            if finding['metric'] == 'category_concentration':
                recommendations.append({
                    'priority': 'medium',
                    'action': '拓展品类销售',
                    'details': f"加强{features.get('category', {}).get('distribution', [['其他品类', 0]])[1][0] if len(features.get('category', {}).get('distribution', [])) > 1 else '其他品类'}等次要品类的学习",
                    'expected_impact': '降低品类集中度，提升综合销售能力'
                })
            elif finding['metric'] == 'low_discount_ratio':
                recommendations.append({
                    'priority': 'medium',
                    'action': '议价能力提升',
                    'details': '学习价值塑造话术、减少不必要的折扣让步、提升正价销售能力',
                    'expected_impact': '低折扣订单占比降至15%以下'
                })
            elif finding['metric'] == 'aiot_data_quality':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'AIoT数据检查',
                    'details': '联系技术团队检查AIoT设备状态、客户行为归因规则、数据同步情况',
                    'expected_impact': '恢复准确的客户分层数据'
                })
            elif finding['metric'] == 'effective_customer_decline':
                recommendations.append({
                    'priority': 'high',
                    'action': '客流提升专项',
                    'details': '加强邀约回店、社群运营、老客带新等引流措施',
                    'expected_impact': '有效客户数恢复至上期水平'
                })

        elif finding['type'] == 'strength' and finding['metric'] == 'new_customer':
            recommendations.append({
                'priority': 'low',
                'action': '经验分享',
                'details': '让该导购分享新客开发经验，带动团队整体提升',
                'expected_impact': '团队新客获取能力整体提升'
            })

    return recommendations


# 便捷函数：批量分析多个导购
def batch_analyze(store_id: str, guide_names: List[str],
                  from_date: str, to_date: str) -> List[Dict]:
    """
    批量分析多个导购
    
    Args:
        store_id: 门店ID
        guide_names: 导购姓名列表
        from_date: 分析开始日期
        to_date: 分析结束日期
    
    Returns:
        List[Dict]: 各导购的分析结果
    """
    results = []
    for name in guide_names:
        result = analyze(store_id, name, from_date, to_date)
        results.append(result)
    return results


def _analyze_trend_14days(store_id: str, guide_name: str,
                          from_date: str, to_date: str) -> Dict:
    """分析14天销售趋势"""
    try:
        client = get_api_client()
        params = {
            'guideName': guide_name,
            'storeId': store_id,
            'fromDate': from_date,
            'toDate': to_date
        }

        response = client.call_api('copilot', '/api/v1/guide/trend14days', params=params)

        trend_data = response.get('trend14Days', [])

        if not trend_data:
            print("  无14天趋势数据")
            return {'has_data': False, 'days': []}

        # 分析趋势数据
        analysis = {
            'has_data': True,
            'total_days': len(trend_data),
            'active_days': 0,  # 有销售的天数
            'zero_days': 0,    # 无销售的天数
            'total_sales': 0,
            'total_orders': 0,
            'avg_daily_sales': 0,
            'avg_daily_orders': 0,
            'peak_day': None,
            'trough_day': None,
            'days': []
        }

        # 计算每日数据
        for day in trend_data:
            sales = day.get('salesAmount', 0)
            orders = day.get('validOrders', 0)
            avg_order = day.get('avgOrder', 0)
            share = day.get('performanceShare', 0)
            
            day_data = {
                'date': day.get('date'),
                'sales': round(sales, 2),
                'orders': orders,
                'avg_order': round(avg_order, 2),
                'share': share
            }
            analysis['days'].append(day_data)
            
            analysis['total_sales'] += sales
            analysis['total_orders'] += orders
            
            if sales > 0:
                analysis['active_days'] += 1
            else:
                analysis['zero_days'] += 1

        # 计算平均值
        if analysis['total_days'] > 0:
            analysis['avg_daily_sales'] = round(analysis['total_sales'] / analysis['total_days'], 2)
            analysis['avg_daily_orders'] = round(analysis['total_orders'] / analysis['total_days'], 2)

        # 找出峰值和谷值
        if analysis['days']:
            sorted_by_sales = sorted(analysis['days'], key=lambda x: x['sales'], reverse=True)
            analysis['peak_day'] = sorted_by_sales[0]
            analysis['trough_day'] = sorted_by_sales[-1]

        # 打印分析结果
        print(f"  统计天数: {analysis['total_days']}天")
        print(f"  有销售天数: {analysis['active_days']}天")
        print(f"  无销售天数: {analysis['zero_days']}天")
        print(f"  日均销售额: ¥{analysis['avg_daily_sales']:,.0f}")
        print(f"  日均订单数: {analysis['avg_daily_orders']:.1f}单")
        
        if analysis['peak_day']:
            print(f"  销售峰值: {analysis['peak_day']['date']} ¥{analysis['peak_day']['sales']:,.0f} ({analysis['peak_day']['orders']}单)")
        if analysis['trough_day'] and analysis['trough_day']['sales'] == 0:
            zero_dates = [d['date'] for d in analysis['days'] if d['sales'] == 0]
            if zero_dates:
                print(f"  无销售日期: {', '.join(zero_dates)}")

        # 打印近7天趋势
        print(f"\n  近7天趋势:")
        recent_7 = analysis['days'][-7:] if len(analysis['days']) >= 7 else analysis['days']
        print(f"  {'日期':<12} {'销售额':>10} {'订单':>4} {'客单价':>8} {'占比':>4}")
        print(f"  {'-'*45}")
        for day in recent_7:
            print(f"  {day['date']:<12} ¥{day['sales']:>8,.0f} {day['orders']:>4}单 ¥{day['avg_order']:>6,.0f} {day['share']:>3}%")

        return analysis

    except Exception as e:
        print(f"  提示: 14天趋势API不可用 - {e}")
        return {'has_data': False, 'days': []}


if __name__ == "__main__":
    # 测试
    result = analyze(
        store_id="416759_1714379448487",
        guide_name="李翠",
        from_date="2026-03-01",
        to_date="2026-03-25"
    )
    
    print("\n最终输出:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
