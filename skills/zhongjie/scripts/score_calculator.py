"""
深圳积分入学计算器

支持区域：宝安区、光明区、龙华区（非大学区）
数据来源：深圳本地宝 2025 年积分入学政策
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


# ── 宝安区配置 ────────────────────────────────────────────────────────────────

BAOAN_BASE_SCORES = {
    ("宝安户籍", "学区购房"): 105,
    ("宝安户籍", "学区租房", "深圳无房"): 95,
    ("宝安户籍", "学区租房", "深圳有房"): 70,
    ("深圳其他区户籍", "学区购房"): 100,
    ("深圳其他区户籍", "学区租房", "深圳无房"): 85,
    ("深圳其他区户籍", "学区租房", "深圳有房"): 65,
    ("非深户籍", "学区购房"): 75,
    ("非深户籍", "学区租房"): 60,
}

# ── 光明区配置 ────────────────────────────────────────────────────────────────

GUANGMING_BASE_SCORES = {
    ("光明户籍", "学区购房"): 90,
    ("光明户籍", "学区租房"): 80,
    ("非学区光明户籍", "学区购房"): 70,
    ("非学区光明户籍", "学区租房"): 60,
    ("深圳其他区户籍", "学区购房"): 50,
    ("深圳其他区户籍", "学区租房"): 40,
    ("非深户籍", "学区购房"): 30,
    ("非深户籍", "学区租房"): 20,
}

# ── 龙华区配置（非大学区） ────────────────────────────────────────────────────

LONGHUA_BASE_SCORE = 60  # 龙华区非大学区统一基础分


@dataclass
class ApplicantInfo:
    """申请人信息"""

    district: str  # 申请区域：宝安 / 光明 / 龙华
    hukou_type: str  # 户籍类型：宝安户籍 / 光明户籍 / 非学区光明户籍 / 深圳其他区户籍 / 非深户籍
    housing_type: str  # 住房类型：学区购房 / 学区租房
    has_other_property: Optional[str] = None  # 深圳有房 / 深圳无房（宝安区深户租房时需要）

    housing_start_date: Optional[date] = None  # 房产证发证日期 或 租赁凭证签发日期
    hukou_move_date: Optional[date] = None  # 户口迁入深圳日期（深户用）
    shebao_months: int = 0  # 养老+医疗同时缴纳的月数（非深户用）
    both_parents_have_cert: bool = False  # 户证加分条件（双方深户 / 一深户一居住证 / 双方居住证）
    apply_date: Optional[date] = None  # 积分计算截止日期，默认当年 4 月 1 日

    school_level: str = "小一"  # 小一 / 初一

    def _cutoff_date(self) -> date:
        if self.apply_date:
            return self.apply_date
        today = date.today()
        return date(today.year, 4, 1)


def _months_between(start: date, end: date) -> int:
    if start >= end:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)


# ── 宝安区计算 ─────────────────────────────────────────────────────────────

def _calc_baoan(info: ApplicantInfo) -> dict:
    is_shenzhen = info.hukou_type in ("宝安户籍", "深圳其他区户籍")
    cutoff = info._cutoff_date()

    # 基础分
    if info.housing_type == "学区购房":
        key = (info.hukou_type, "学区购房")
    elif is_shenzhen and info.has_other_property:
        key = (info.hukou_type, "学区租房", info.has_other_property)
    else:
        key = (info.hukou_type, "学区租房")

    base = BAOAN_BASE_SCORES.get(key, 0)

    # 加分
    housing_bonus = 0.0
    shebao_bonus = 0.0
    extra_shebao_bonus = 0.0
    cert_bonus = 0.0

    if is_shenzhen:
        if info.housing_start_date:
            months = _months_between(info.housing_start_date, cutoff)
            housing_bonus = round(months * 0.1, 1)
    else:
        if info.shebao_months > 0:
            shebao_bonus = round(info.shebao_months * 0.1, 1)
        if info.school_level == "小一" and info.shebao_months >= 60:
            extra_shebao_bonus = 1.0

    if info.both_parents_have_cert:
        cert_bonus = 0.5

    total_bonus = round(housing_bonus + shebao_bonus + extra_shebao_bonus + cert_bonus, 1)
    total = round(base + total_bonus, 1)

    return {
        "区域": "宝安区",
        "基础分": base,
        "居住时间加分": housing_bonus,
        "社保时间加分": shebao_bonus,
        "社保满5年额外加分": extra_shebao_bonus,
        "户证情况加分": cert_bonus,
        "加分小计": total_bonus,
        "综合积分": total,
    }


# ── 光明区计算 ─────────────────────────────────────────────────────────────

def _calc_guangming(info: ApplicantInfo) -> dict:
    is_shenzhen = info.hukou_type in ("光明户籍", "非学区光明户籍", "深圳其他区户籍")
    cutoff = info._cutoff_date()

    key = (info.hukou_type, info.housing_type)
    base = GUANGMING_BASE_SCORES.get(key, 0)

    hukou_bonus = 0.0
    housing_bonus = 0.0
    shebao_bonus = 0.0
    dual_cert_bonus = 0.0

    if is_shenzhen and info.hukou_move_date:
        hukou_bonus = round(_months_between(info.hukou_move_date, cutoff) * 0.1, 1)

    if info.housing_start_date:
        housing_bonus = round(_months_between(info.housing_start_date, cutoff) * 0.1, 1)

    if not is_shenzhen and info.shebao_months > 0:
        shebao_bonus = round(info.shebao_months * 0.1, 1)

    if not is_shenzhen and info.both_parents_have_cert:
        dual_cert_bonus = 1.0

    total_bonus = round(hukou_bonus + housing_bonus + shebao_bonus + dual_cert_bonus, 1)
    total = round(base + total_bonus, 1)

    return {
        "区域": "光明区",
        "基础分": base,
        "入户时长加分": hukou_bonus,
        "居住时长加分": housing_bonus,
        "社保加分": shebao_bonus,
        "双居住证加分": dual_cert_bonus,
        "加分小计": total_bonus,
        "综合积分": total,
    }


# ── 龙华区计算（非大学区） ─────────────────────────────────────────────────

def _calc_longhua(info: ApplicantInfo) -> dict:
    is_shenzhen = info.hukou_type in ("深圳其他区户籍",) or "龙华" in info.hukou_type or "深圳" in info.hukou_type
    if info.hukou_type == "非深户籍":
        is_shenzhen = False
    cutoff = info._cutoff_date()

    base = LONGHUA_BASE_SCORE

    housing_bonus = 0.0
    hukou_bonus = 0.0
    shebao_bonus = 0.0

    if info.housing_start_date:
        housing_bonus = round(_months_between(info.housing_start_date, cutoff) * 0.1, 1)

    if is_shenzhen and info.hukou_move_date:
        hukou_bonus = round(_months_between(info.hukou_move_date, cutoff) * 0.1, 1)

    if not is_shenzhen and info.shebao_months > 0:
        shebao_bonus = round(info.shebao_months * 0.1, 1)

    total_bonus = round(housing_bonus + hukou_bonus + shebao_bonus, 1)
    total = round(base + total_bonus, 1)

    return {
        "区域": "龙华区（非大学区）",
        "基础分": base,
        "居住情况加分": housing_bonus,
        "户籍迁入加分": hukou_bonus,
        "社保加分": shebao_bonus,
        "加分小计": total_bonus,
        "综合积分": total,
    }


# ── 统一入口 ──────────────────────────────────────────────────────────────

DISTRICT_CALCULATORS = {
    "宝安": _calc_baoan,
    "光明": _calc_guangming,
    "龙华": _calc_longhua,
}


def calculate(info: ApplicantInfo) -> dict:
    calculator = DISTRICT_CALCULATORS.get(info.district)
    if not calculator:
        raise ValueError(f"暂不支持 [{info.district}] 区，目前支持：{list(DISTRICT_CALCULATORS.keys())}")
    return calculator(info)


def print_result(result: dict):
    print("=" * 50)
    print(f"  积分入学计算结果 —— {result['区域']}")
    print("=" * 50)
    for k, v in result.items():
        if k == "区域":
            continue
        label = f"  {k}"
        if k == "综合积分":
            print("-" * 50)
            print(f"  ★ {k}: {v} 分")
        else:
            print(f"  {label}: {v} 分")
    print("=" * 50)


# ── 使用示例 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n【场景1】宝安户籍 + 学区购房，房产证 5 年")
    result = calculate(ApplicantInfo(
        district="宝安",
        hukou_type="宝安户籍",
        housing_type="学区购房",
        housing_start_date=date(2021, 6, 1),
        both_parents_have_cert=True,
        apply_date=date(2027, 4, 1),
    ))
    print_result(result)

    print("\n【场景2】深圳其他区户籍 + 学区租房 + 深圳无房，租赁 3 年")
    result = calculate(ApplicantInfo(
        district="宝安",
        hukou_type="深圳其他区户籍",
        housing_type="学区租房",
        has_other_property="深圳无房",
        housing_start_date=date(2024, 4, 1),
        both_parents_have_cert=True,
        apply_date=date(2027, 4, 1),
    ))
    print_result(result)

    print("\n【场景3】非深户 + 学区购房，社保 6 年")
    result = calculate(ApplicantInfo(
        district="宝安",
        hukou_type="非深户籍",
        housing_type="学区购房",
        shebao_months=72,
        both_parents_have_cert=True,
        apply_date=date(2027, 4, 1),
    ))
    print_result(result)

    print("\n【场景4】光明区 —— 深圳其他区户籍 + 学区购房")
    result = calculate(ApplicantInfo(
        district="光明",
        hukou_type="深圳其他区户籍",
        housing_type="学区购房",
        housing_start_date=date(2022, 1, 1),
        hukou_move_date=date(2018, 6, 1),
        apply_date=date(2027, 4, 30),
    ))
    print_result(result)

    print("\n【场景5】龙华区 —— 深圳户籍 + 购房 3 年 + 入户 8 年")
    result = calculate(ApplicantInfo(
        district="龙华",
        hukou_type="深圳其他区户籍",
        housing_type="学区购房",
        housing_start_date=date(2024, 3, 1),
        hukou_move_date=date(2019, 3, 1),
        apply_date=date(2027, 3, 31),
    ))
    print_result(result)
