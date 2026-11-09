"""货损鉴定：残值、免赔、责任分摊和索赔时效。金额是分，时间是小时。"""

from typing import Dict, List, Sequence, Tuple


# 货类 -> (新货月折旧千分比, 残值下限千分比, 通知时限小时, 免赔千分比)
POLICY: Dict[str, Tuple[int, int, int, int]] = {
    "冻肉": (15, 200, 24, 20),
    "冻鱼": (18, 150, 24, 20),
    "香蕉": (40, 0, 12, 50),
    "药品": (8, 300, 6, 0),
    "电器": (12, 200, 48, 30),
    "家具": (6, 250, 72, 40),
    "钢材": (2, 400, 72, 10),
    "纸浆": (5, 200, 48, 20),
}

LIABLE = ("承运人", "码头", "托运人", "保险人")


class SurveyError(ValueError):
    """鉴定数据不合法。"""


def sound_value(cargo: str, invoice_cents: int, age_months: int) -> int:
    """按月折旧后的完好价值，不低于保单残值下限。"""
    if cargo not in POLICY:
        raise SurveyError("货类没有保单")
    if invoice_cents < 0 or age_months < 0:
        raise SurveyError("发票或月龄不合法")
    rate, floor, _notice, _deduct = POLICY[cargo]
    kept = 1000 - rate * age_months
    if kept < floor:
        kept = floor
    return invoice_cents * kept // 1000


def damage_ratio(sound_packages: int, damaged_packages: int, grade: str) -> int:
    """返回损失千分比。等级决定受损箱里有多少比例算全损。"""
    if sound_packages < 0 or damaged_packages < 0:
        raise SurveyError("件数不能为负")
    total = sound_packages + damaged_packages
    if total == 0:
        raise SurveyError("没有件数")
    factor = {"表面": 200, "部分": 600, "全损": 1000, "短少": 1000}
    if grade not in factor:
        raise SurveyError("损失等级不存在")
    return damaged_packages * factor[grade] // total


def gross_loss(cargo: str, invoice_cents: int, age_months: int, sound_packages: int, damaged_packages: int, grade: str) -> int:
    base = sound_value(cargo, invoice_cents, age_months)
    return base * damage_ratio(sound_packages, damaged_packages, grade) // 1000


def salvage(gross_cents: int, sold_cents: int, auction_fee_cents: int) -> int:
    """残值变卖冲减损失。拍卖费用先从卖价里扣，卖价不够付费用时不倒贴。"""
    if min(gross_cents, sold_cents, auction_fee_cents) < 0:
        raise SurveyError("残值参数不合法")
    net = sold_cents - auction_fee_cents
    if net < 0:
        net = 0
    if net > gross_cents:
        return 0
    return gross_cents - net


def deductible(cargo: str, loss_cents: int) -> int:
    _rate, _floor, _notice, permille = POLICY[cargo]
    if loss_cents < 0:
        raise SurveyError("损失不能为负")
    return loss_cents * permille // 1000


def payable(cargo: str, invoice_cents: int, age_months: int, sound_packages: int, damaged_packages: int, grade: str, sold_cents: int, auction_fee_cents: int) -> int:
    gross = gross_loss(cargo, invoice_cents, age_months, sound_packages, damaged_packages, grade)
    after_salvage = salvage(gross, sold_cents, auction_fee_cents)
    deduct = deductible(cargo, after_salvage)
    remain = after_salvage - deduct
    return remain if remain > 0 else 0


def split_liability(amount: int, shares: Sequence[Tuple[str, int]]) -> List[Tuple[str, int]]:
    """按千分比分摊。千分比必须加总为 1000，最后一方吃掉整除余数。"""
    if amount < 0:
        raise SurveyError("金额不能为负")
    if not shares:
        raise SurveyError("没有责任方")
    names = []
    total = 0
    for name, permille in shares:
        if name not in LIABLE:
            raise SurveyError("责任方不存在")
        if name in names:
            raise SurveyError("责任方重复")
        if type(permille) is not int or permille < 0:
            raise SurveyError("分摊比例不合法")
        names.append(name)
        total += permille
    if total != 1000:
        raise SurveyError("分摊必须凑满千分之一千")
    result: List[Tuple[str, int]] = []
    consumed = 0
    for index, (name, permille) in enumerate(shares):
        if index == len(shares) - 1:
            part = amount - consumed
        else:
            part = amount * permille // 1000
            consumed += part
        result.append((name, part))
    return result


def notice_status(cargo: str, discovered_hour: int, notified_hour: int) -> str:
    """通知时限从发现当小时起算，超时仍可索赔，但标记为迟通知。"""
    _rate, _floor, limit, _deduct = POLICY[cargo]
    if notified_hour < discovered_hour:
        raise SurveyError("通知早于发现")
    if notified_hour - discovered_hour <= limit:
        return "按时"
    return "迟通知"


def time_barred(discharge_hour: int, filed_hour: int, months: int = 12) -> bool:
    """诉讼时效默认 12 个月，按 30 天一个月、24 小时一天折算。届满当小时仍有效。"""
    if filed_hour < discharge_hour or months <= 0:
        raise SurveyError("时效参数不合法")
    return filed_hour - discharge_hour > months * 30 * 24


def photo_gaps(cargo: str, grade: str, photos: Sequence[str]) -> List[str]:
    """不同等级要求的照片科目。返回还缺的科目。"""
    required = {
        "表面": ("箱体外观", "封志", "标签"),
        "部分": ("箱体外观", "封志", "内部", "温度"),
        "全损": ("箱体外观", "封志", "内部", "温度", "销毁"),
        "短少": ("箱体外观", "封志", "理货"),
    }
    if grade not in required:
        raise SurveyError("损失等级不存在")
    if cargo not in POLICY:
        raise SurveyError("货类没有保单")
    have = {item.strip() for item in photos}
    extra: Tuple[str, ...] = ()
    if cargo in ("冻肉", "冻鱼", "香蕉", "药品") and grade != "短少":
        extra = ("温度记录",)
    needed = required[grade] + extra
    return [item for item in needed if item not in have]


def survey_report(
    cargo: str,
    invoice_cents: int,
    age_months: int,
    sound_packages: int,
    damaged_packages: int,
    grade: str,
    sold_cents: int,
    auction_fee_cents: int,
    shares: Sequence[Tuple[str, int]],
    discovered_hour: int,
    notified_hour: int,
    discharge_hour: int,
    filed_hour: int,
    photos: Sequence[str],
) -> Dict[str, object]:
    amount = payable(
        cargo,
        invoice_cents,
        age_months,
        sound_packages,
        damaged_packages,
        grade,
        sold_cents,
        auction_fee_cents,
    )
    gaps = photo_gaps(cargo, grade, photos)
    barred = time_barred(discharge_hour, filed_hour)
    if gaps or barred:
        amount = 0
    return {
        "货类": cargo,
        "完好价值": sound_value(cargo, invoice_cents, age_months),
        "赔付": amount,
        "分摊": split_liability(amount, shares),
        "通知": notice_status(cargo, discovered_hour, notified_hour),
        "时效": "已过" if barred else "未过",
        "缺照片": gaps,
    }
