#!/usr/bin/env python3
"""
地理位置数据和匹配逻辑。

设计原则：
- 层级结构：city → province → country
- 覆盖全球主要技术中心
- 短缩写仅保留全球广泛认可的（cn, sg, hk, tw, jp, uk, us）
- 中文启发式作为最后回落（仅 china 目标）
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict


@dataclass
class LocationTarget:
    """JD Parser 解析出的目标地理位置"""
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    raw: str = ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 全球地理位置层级数据
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 结构: { country_key: { "names": [...], "codes": [...], "provinces": { ... } } }
# province 结构: { province_key: { "names": [...], "cities": { city_key: [...aliases] } } }

COUNTRIES: Dict = {
    "china": {
        "names": ["中国", "china", "chinese"],
        "codes": ["cn"],
        "provinces": {
            # 直辖市（省=市）
            "beijing": {
                "names": ["北京", "beijing"],
                "cities": {"beijing": ["北京", "beijing", "peking"]}
            },
            "shanghai": {
                "names": ["上海", "shanghai"],
                "cities": {"shanghai": ["上海", "shanghai"]}
            },
            "tianjin": {
                "names": ["天津", "tianjin"],
                "cities": {"tianjin": ["天津", "tianjin"]}
            },
            "chongqing": {
                "names": ["重庆", "chongqing"],
                "cities": {"chongqing": ["重庆", "chongqing"]}
            },
            # 广东
            "guangdong": {
                "names": ["广东", "guangdong"],
                "cities": {
                    "shenzhen": ["深圳", "shenzhen"],
                    "guangzhou": ["广州", "guangzhou", "canton"],
                    "dongguan": ["东莞", "dongguan"],
                    "foshan": ["佛山", "foshan"],
                    "zhuhai": ["珠海", "zhuhai"],
                    "zhongshan": ["中山", "zhongshan"],
                    "huizhou": ["惠州", "huizhou"],
                }
            },
            # 浙江
            "zhejiang": {
                "names": ["浙江", "zhejiang"],
                "cities": {
                    "hangzhou": ["杭州", "hangzhou"],
                    "ningbo": ["宁波", "ningbo"],
                    "wenzhou": ["温州", "wenzhou"],
                    "jiaxing": ["嘉兴", "jiaxing"],
                    "shaoxing": ["绍兴", "shaoxing"],
                }
            },
            # 江苏
            "jiangsu": {
                "names": ["江苏", "jiangsu"],
                "cities": {
                    "nanjing": ["南京", "nanjing", "nanking"],
                    "suzhou": ["苏州", "suzhou"],
                    "wuxi": ["无锡", "wuxi"],
                    "changzhou": ["常州", "changzhou"],
                    "nantong": ["南通", "nantong"],
                }
            },
            # 四川
            "sichuan": {
                "names": ["四川", "sichuan"],
                "cities": {
                    "chengdu": ["成都", "chengdu"],
                    "mianyang": ["绵阳", "mianyang"],
                }
            },
            # 湖北
            "hubei": {
                "names": ["湖北", "hubei"],
                "cities": {
                    "wuhan": ["武汉", "wuhan"],
                }
            },
            # 湖南
            "hunan": {
                "names": ["湖南", "hunan"],
                "cities": {
                    "changsha": ["长沙", "changsha"],
                }
            },
            # 陕西
            "shaanxi": {
                "names": ["陕西", "shaanxi"],
                "cities": {
                    "xian": ["西安", "xian", "xi'an"],
                }
            },
            # 福建
            "fujian": {
                "names": ["福建", "fujian"],
                "cities": {
                    "fuzhou": ["福州", "fuzhou"],
                    "xiamen": ["厦门", "xiamen", "amoy"],
                    "quanzhou": ["泉州", "quanzhou"],
                }
            },
            # 山东
            "shandong": {
                "names": ["山东", "shandong"],
                "cities": {
                    "jinan": ["济南", "jinan"],
                    "qingdao": ["青岛", "qingdao"],
                }
            },
            # 河南
            "henan": {
                "names": ["河南", "henan"],
                "cities": {
                    "zhengzhou": ["郑州", "zhengzhou"],
                }
            },
            # 安徽
            "anhui": {
                "names": ["安徽", "anhui"],
                "cities": {
                    "hefei": ["合肥", "hefei"],
                }
            },
            # 辽宁
            "liaoning": {
                "names": ["辽宁", "liaoning"],
                "cities": {
                    "shenyang": ["沈阳", "shenyang"],
                    "dalian": ["大连", "dalian"],
                }
            },
            # 吉林
            "jilin": {
                "names": ["吉林", "jilin"],
                "cities": {
                    "changchun": ["长春", "changchun"],
                }
            },
            # 黑龙江
            "heilongjiang": {
                "names": ["黑龙江", "heilongjiang"],
                "cities": {
                    "harbin": ["哈尔滨", "harbin"],
                }
            },
            # 河北
            "hebei": {
                "names": ["河北", "hebei"],
                "cities": {
                    "shijiazhuang": ["石家庄", "shijiazhuang"],
                }
            },
            # 云南
            "yunnan": {
                "names": ["云南", "yunnan"],
                "cities": {
                    "kunming": ["昆明", "kunming"],
                }
            },
            # 贵州
            "guizhou": {
                "names": ["贵州", "guizhou"],
                "cities": {
                    "guiyang": ["贵阳", "guiyang"],
                }
            },
            # 广西
            "guangxi": {
                "names": ["广西", "guangxi"],
                "cities": {
                    "nanning": ["南宁", "nanning"],
                }
            },
            # 海南
            "hainan": {
                "names": ["海南", "hainan"],
                "cities": {
                    "haikou": ["海口", "haikou"],
                    "sanya": ["三亚", "sanya"],
                }
            },
            # 甘肃
            "gansu": {
                "names": ["甘肃", "gansu"],
                "cities": {"lanzhou": ["兰州", "lanzhou"]}
            },
            # 内蒙古
            "inner_mongolia": {
                "names": ["内蒙古", "inner mongolia"],
                "cities": {"hohhot": ["呼和浩特", "hohhot"]}
            },
            # 新疆
            "xinjiang": {
                "names": ["新疆", "xinjiang"],
                "cities": {"urumqi": ["乌鲁木齐", "urumqi"]}
            },
            # 宁夏
            "ningxia": {
                "names": ["宁夏", "ningxia"],
                "cities": {"yinchuan": ["银川", "yinchuan"]}
            },
            # 青海
            "qinghai": {
                "names": ["青海", "qinghai"],
                "cities": {"xining": ["西宁", "xining"]}
            },
            # 西藏
            "tibet": {
                "names": ["西藏", "tibet"],
                "cities": {"lhasa": ["拉萨", "lhasa"]}
            },
            # 港澳台
            "hong_kong": {
                "names": ["香港", "hong kong", "hongkong"],
                "cities": {"hong_kong": ["香港", "hong kong", "hongkong"]}
            },
            "taiwan": {
                "names": ["台湾", "taiwan"],
                "cities": {
                    "taipei": ["台北", "taipei"],
                    "taichung": ["台中", "taichung"],
                    "kaohsiung": ["高雄", "kaohsiung"],
                    "tainan": ["台南", "tainan"],
                    "hsinchu": ["新竹", "hsinchu"],
                }
            },
            "macau": {
                "names": ["澳门", "macau", "macao"],
                "cities": {"macau": ["澳门", "macau", "macao"]}
            },
        }
    },

    "singapore": {
        "names": ["新加坡", "singapore", "singaporean"],
        "codes": ["sg"],
        "provinces": {}
    },

    "japan": {
        "names": ["日本", "japan", "japanese"],
        "codes": ["jp"],
        "provinces": {
            "tokyo": {
                "names": ["東京", "东京", "tokyo"],
                "cities": {"tokyo": ["東京", "东京", "tokyo"]}
            },
            "osaka": {
                "names": ["大阪", "osaka"],
                "cities": {"osaka": ["大阪", "osaka"]}
            },
            "kyoto": {
                "names": ["京都", "kyoto"],
                "cities": {"kyoto": ["京都", "kyoto"]}
            },
            "fukuoka": {
                "names": ["福岡", "福冈", "fukuoka"],
                "cities": {"fukuoka": ["福岡", "福冈", "fukuoka"]}
            },
            "yokohama": {
                "names": ["横浜", "横滨", "yokohama"],
                "cities": {"yokohama": ["横浜", "横滨", "yokohama"]}
            },
        }
    },

    "south_korea": {
        "names": ["韩国", "south korea", "korea", "korean"],
        "codes": ["kr"],
        "provinces": {
            "seoul": {
                "names": ["首尔", "서울", "seoul"],
                "cities": {"seoul": ["首尔", "서울", "seoul"]}
            },
            "busan": {
                "names": ["釜山", "부산", "busan"],
                "cities": {"busan": ["釜山", "부산", "busan"]}
            },
        }
    },

    "usa": {
        "names": ["美国", "united states", "america"],
        "codes": ["us", "usa"],
        "provinces": {
            "california": {
                "names": ["加州", "california", "ca"],
                "cities": {
                    "san_francisco": ["旧金山", "san francisco", "sf", "bay area"],
                    "los_angeles": ["洛杉矶", "los angeles", "la"],
                    "san_jose": ["san jose", "圣何塞"],
                    "palo_alto": ["palo alto"],
                    "mountain_view": ["mountain view"],
                    "san_diego": ["san diego", "圣地亚哥"],
                }
            },
            "washington": {
                "names": ["华盛顿州", "washington"],
                "cities": {
                    "seattle": ["西雅图", "seattle"],
                    "redmond": ["redmond"],
                }
            },
            "new_york": {
                "names": ["纽约州", "new york"],
                "cities": {
                    "new_york_city": ["纽约", "new york", "nyc", "new york city"],
                }
            },
            "texas": {
                "names": ["德州", "texas"],
                "cities": {
                    "austin": ["奥斯汀", "austin"],
                    "dallas": ["达拉斯", "dallas"],
                }
            },
            "massachusetts": {
                "names": ["马萨诸塞", "massachusetts"],
                "cities": {
                    "boston": ["波士顿", "boston"],
                    "cambridge": ["剑桥", "cambridge"],
                }
            },
        }
    },

    "uk": {
        "names": ["英国", "united kingdom", "britain"],
        "codes": ["uk", "gb"],
        "provinces": {
            "england": {
                "names": ["英格兰", "england"],
                "cities": {
                    "london": ["伦敦", "london"],
                    "cambridge": ["剑桥", "cambridge"],
                    "manchester": ["曼彻斯特", "manchester"],
                }
            },
        }
    },

    "germany": {
        "names": ["德国", "germany", "deutschland"],
        "codes": ["de"],
        "provinces": {
            "berlin": {
                "names": ["柏林", "berlin"],
                "cities": {"berlin": ["柏林", "berlin"]}
            },
            "bavaria": {
                "names": ["巴伐利亚", "bavaria", "bayern"],
                "cities": {"munich": ["慕尼黑", "munich", "münchen"]}
            },
        }
    },

    "india": {
        "names": ["印度", "india", "indian"],
        "codes": ["in"],
        "provinces": {
            "karnataka": {
                "names": ["卡纳塔克", "karnataka"],
                "cities": {"bangalore": ["班加罗尔", "bangalore", "bengaluru"]}
            },
            "telangana": {
                "names": ["特伦甘纳", "telangana"],
                "cities": {"hyderabad": ["海得拉巴", "hyderabad"]}
            },
            "maharashtra": {
                "names": ["马哈拉施特拉", "maharashtra"],
                "cities": {
                    "mumbai": ["孟买", "mumbai", "bombay"],
                    "pune": ["浦那", "pune"],
                }
            },
            "delhi": {
                "names": ["德里", "delhi"],
                "cities": {"delhi": ["德里", "delhi", "new delhi"]}
            },
        }
    },

    "canada": {
        "names": ["加拿大", "canada", "canadian"],
        "codes": ["ca"],
        "provinces": {
            "ontario": {
                "names": ["安大略", "ontario"],
                "cities": {
                    "toronto": ["多伦多", "toronto"],
                    "waterloo": ["滑铁卢", "waterloo"],
                    "ottawa": ["渥太华", "ottawa"],
                }
            },
            "british_columbia": {
                "names": ["不列颠哥伦比亚", "british columbia", "bc"],
                "cities": {"vancouver": ["温哥华", "vancouver"]}
            },
        }
    },

    "australia": {
        "names": ["澳大利亚", "australia", "australian"],
        "codes": ["au"],
        "provinces": {
            "nsw": {
                "names": ["新南威尔士", "new south wales", "nsw"],
                "cities": {"sydney": ["悉尼", "sydney"]}
            },
            "victoria": {
                "names": ["维多利亚", "victoria"],
                "cities": {"melbourne": ["墨尔本", "melbourne"]}
            },
        }
    },

    # 区域聚合
    "southeast_asia": {
        "names": ["东南亚", "southeast asia", "sea"],
        "codes": [],
        "provinces": {}
    },
}

# 港澳台的特殊短码
SPECIAL_CODES = {
    "hk": ("china", "hong_kong"),
    "tw": ("china", "taiwan"),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 内部查找索引（启动时构建，O(1) 查找）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# alias → (country, province, city) 的反向索引
_ALIAS_INDEX: Dict[str, Tuple[str, Optional[str], Optional[str]]] = {}


def _build_index():
    """构建别名反向索引"""
    for country_key, country_data in COUNTRIES.items():
        # 国家名和代码
        for name in country_data["names"]:
            _ALIAS_INDEX[name.lower()] = (country_key, None, None)
        for code in country_data.get("codes", []):
            _ALIAS_INDEX[code.lower()] = (country_key, None, None)

        # 省份和城市
        for prov_key, prov_data in country_data.get("provinces", {}).items():
            for name in prov_data["names"]:
                _ALIAS_INDEX[name.lower()] = (country_key, prov_key, None)
            for city_key, city_aliases in prov_data.get("cities", {}).items():
                for alias in city_aliases:
                    _ALIAS_INDEX[alias.lower()] = (country_key, prov_key, city_key)

    # 特殊短码
    for code, (country, province) in SPECIAL_CODES.items():
        _ALIAS_INDEX[code.lower()] = (country, province, None)


_build_index()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 公共 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def resolve_location(raw: str) -> Optional[LocationTarget]:
    """
    将 JD Parser 输出的 location 字符串解析为 LocationTarget。

    支持输入：
    - 城市名（中英文）: "深圳", "shenzhen"
    - 省份名: "guangdong", "广东"
    - 国家名: "china", "日本"
    - 短码: "hk", "sg"
    - 多城市: "shanghai,hong kong"（取第一个作为主目标）
    - null / "" → None

    返回:
    - LocationTarget 或 None（不限地区）

    Examples:
    >>> resolve_location("深圳")
    LocationTarget(city="shenzhen", province="guangdong", country="china", raw="深圳")
    >>> resolve_location("china")
    LocationTarget(country="china", raw="china")
    >>> resolve_location("")
    None
    """
    if not raw or raw.strip().lower() in ("null", "none", ""):
        return None

    raw = raw.strip()
    # 多城市时取第一个
    first_loc = raw.split(",")[0].strip()
    key = first_loc.lower()

    # 在索引中查找
    if key in _ALIAS_INDEX:
        country, province, city = _ALIAS_INDEX[key]
        return LocationTarget(city=city, province=province, country=country, raw=raw)

    # 尝试模糊匹配（location 字符串可能包含多部分如 "Beijing, China"）
    for alias, (country, province, city) in _ALIAS_INDEX.items():
        if alias in key or key in alias:
            return LocationTarget(city=city, province=province, country=country, raw=raw)

    # 无法解析时，作为国家级兜底
    return LocationTarget(country=key, raw=raw)


def match_location(
    user_location: str,
    user_name: str,
    user_bio: str,
    target: LocationTarget,
    strict: bool = False,
) -> Tuple[bool, str]:
    """
    匹配用户的地理位置。

    strict=False（默认，宽松模式）：层级回落 city → province → country → 中文启发式
    strict=True（严格模式）：仅匹配指定城市/省份，不回落到国家级。Remote 仍然通过。

    匹配顺序:
    0. Remote → 直接通过（两种模式均通过）
    1. 精确城市匹配
    2. 省份匹配（严格模式下，这是最宽的范围）
    3. 国家回落（仅宽松模式）
    4. 中文启发式（仅宽松模式 + country=china）
    5. 不匹配

    Returns:
        (matched: bool, reason: str)
    """
    loc_lower = (user_location or "").lower()

    # 规则 0: Remote 通过（仅宽松模式）
    # 严格模式下不通过：用户说"必须是北京"时，不想看到 Remote 的人
    if "remote" in loc_lower and not strict:
        return True, "remote"

    # 规则 1: 精确城市匹配
    if target.city:
        city_aliases = _get_city_aliases(target.country, target.province, target.city)
        if _text_contains_any(loc_lower, city_aliases):
            return True, f"city:{target.city}"

    # 规则 2: 省份匹配
    if target.province:
        prov_aliases = _get_province_aliases(target.country, target.province)
        if _text_contains_any(loc_lower, prov_aliases):
            return True, f"province:{target.province}"
        # 也检查该省所有城市
        all_city_aliases = _get_all_city_aliases_in_province(target.country, target.province)
        if _text_contains_any(loc_lower, all_city_aliases):
            return True, f"province:{target.province}"

    # ── 严格模式到此为止，不回落到国家 ──
    if strict:
        return False, "no_match"

    # 规则 3: 国家回落（仅宽松模式）
    if target.country:
        country_aliases = _get_country_aliases(target.country)
        if _text_contains_any(loc_lower, country_aliases):
            return True, f"country:{target.country}"
        all_aliases = _get_all_aliases_in_country(target.country)
        if _text_contains_any(loc_lower, all_aliases):
            return True, f"country:{target.country}"

    # 规则 4: 中文启发式（仅宽松模式 + china）
    if target.country == "china":
        if _has_chinese(user_name) or _has_chinese(user_bio):
            return True, "chinese_detected"

    return False, "no_match"


def build_user_search_locations(target: LocationTarget) -> List[str]:
    """
    根据 LocationTarget 生成 User Search 的 location 参数列表。
    包含中英文变体，因为 GitHub User Search location: 是整词文本匹配。

    Examples:
    >>> build_user_search_locations(LocationTarget(city="shenzhen", province="guangdong", country="china"))
    ["shenzhen", "深圳", "guangdong", "china"]
    >>> build_user_search_locations(LocationTarget(country="singapore"))
    ["singapore", "新加坡"]
    """
    locations = []
    seen = set()

    def _add(name: str):
        if name.lower() not in seen:
            seen.add(name.lower())
            locations.append(name)

    # 城市级别（最精确）
    if target.city:
        city_aliases = _get_city_aliases(target.country, target.province, target.city)
        for alias in city_aliases:
            _add(alias)

    # 省份级别
    if target.province:
        prov_aliases = _get_province_aliases(target.country, target.province)
        for alias in prov_aliases:
            _add(alias)

    # 国家级别（最宽泛）
    if target.country:
        country_aliases = _get_country_aliases(target.country)
        for alias in country_aliases:
            _add(alias)

    return locations


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 内部辅助函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _has_chinese(text: str) -> bool:
    """检测文本是否包含中文字符"""
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def _text_contains_any(text: str, aliases: List[str]) -> bool:
    """检查 text 是否包含任一别名（大小写不敏感）"""
    text_lower = text.lower()
    for alias in aliases:
        if alias.lower() in text_lower:
            return True
    return False


def _get_country_aliases(country_key: str) -> List[str]:
    """获取国家的所有别名"""
    country = COUNTRIES.get(country_key, {})
    aliases = list(country.get("names", []))
    aliases.extend(country.get("codes", []))
    return aliases


def _get_province_aliases(country_key: str, province_key: str) -> List[str]:
    """获取省份的所有别名"""
    country = COUNTRIES.get(country_key, {})
    province = country.get("provinces", {}).get(province_key, {})
    return list(province.get("names", []))


def _get_city_aliases(country_key: str, province_key: str, city_key: str) -> List[str]:
    """获取城市的所有别名"""
    country = COUNTRIES.get(country_key, {})
    province = country.get("provinces", {}).get(province_key, {})
    return list(province.get("cities", {}).get(city_key, []))


def _get_all_city_aliases_in_province(country_key: str, province_key: str) -> List[str]:
    """获取一个省份下所有城市的别名"""
    country = COUNTRIES.get(country_key, {})
    province = country.get("provinces", {}).get(province_key, {})
    aliases = []
    for city_aliases in province.get("cities", {}).values():
        aliases.extend(city_aliases)
    return aliases


def _get_all_aliases_in_country(country_key: str) -> List[str]:
    """获取一个国家下所有省份和城市的别名"""
    country = COUNTRIES.get(country_key, {})
    aliases = list(country.get("names", []))
    aliases.extend(country.get("codes", []))
    for prov_data in country.get("provinces", {}).values():
        aliases.extend(prov_data.get("names", []))
        for city_aliases in prov_data.get("cities", {}).values():
            aliases.extend(city_aliases)
    return aliases


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI（用于测试）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python location_data.py <location>")
        print("Example: python location_data.py 深圳")
        sys.exit(1)

    raw = sys.argv[1]
    target = resolve_location(raw)
    if target:
        print(f"Resolved: {target}")
        print(f"User Search locations: {build_user_search_locations(target)}")
    else:
        print("Location: 不限地区 (None)")
