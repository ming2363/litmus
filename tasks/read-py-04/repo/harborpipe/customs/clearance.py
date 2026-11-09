"""进口申报：估价、税额、单证和状态机。金额单位是分，时间是小时。"""

from typing import Dict, List, Optional, Sequence, Tuple


# 税号 -> (关税率千分比, 增值税率千分比, 消费税率千分比, 需要的监管证件)
HS: Dict[str, Tuple[int, int, int, Tuple[str, ...]]] = {
    "0202": (120, 90, 0, ("卫生",)),
    "0303": (100, 90, 0, ("卫生",)),
    "0803": (80, 90, 0, ("植检",)),
    "1601": (150, 130, 0, ("卫生", "标签")),
    "2203": (0, 130, 250, ("卫生", "标签")),
    "3002": (0, 90, 0, ("药监", "冷链")),
    "3004": (30, 90, 0, ("药监",)),
    "3808": (60, 130, 0, ("危包",)),
    "8418": (80, 130, 0, ("能效",)),
    "8703": (150, 130, 100, ("3C", "环评")),
    "9403": (0, 130, 0, ()),
    "9503": (0, 130, 0, ("3C",)),
}

DOCUMENTS = {
    "普通": ("合同", "发票", "装箱单", "提单"),
    "冷链": ("合同", "发票", "装箱单", "提单", "温度记录"),
    "危包": ("合同", "发票", "装箱单", "提单", "危包证明"),
    "退运": ("合同", "发票", "装箱单", "原出口报关单"),
}

TRANSITIONS = {
    "草稿": ("已申报", "作废"),
    "已申报": ("审单", "退单"),
    "审单": ("待缴税", "查验", "退单"),
    "查验": ("待缴税", "扣留", "退单"),
    "待缴税": ("已放行",),
    "扣留": ("查验", "退单"),
    "退单": ("草稿", "作废"),
    "已放行": (),
    "作废": (),
}


class ClearanceError(ValueError):
    """申报数据不合法。"""


def lookup_hs(code: str) -> Tuple[int, int, int, Tuple[str, ...]]:
    text = code.strip()
    if len(text) < 4 or text[:4] not in HS:
        raise ClearanceError("税号不在价目里")
    return HS[text[:4]]


def transaction_value(invoice_cents: int, freight_cents: int, insurance_cents: int) -> int:
    """成交价格法：发票加运费加保险，都是到岸前已经发生的金额。"""
    for name, value in (("发票", invoice_cents), ("运费", freight_cents), ("保险", insurance_cents)):
        if type(value) is not int or value < 0:
            raise ClearanceError(name + "不是非负整数分")
    return invoice_cents + freight_cents + insurance_cents


def identical_value(samples: Sequence[int]) -> Optional[int]:
    """相同货物法：取最近三笔正数成交价的中位数。样本不足时返回空。"""
    usable = [item for item in samples if type(item) is int and item > 0]
    if len(usable) < 3:
        return None
    recent = usable[-3:]
    recent.sort()
    return recent[1]


def similar_value(samples: Sequence[Tuple[int, int]], quantity: int) -> Optional[int]:
    """类似货物法：按单价最接近的一笔放大到本票数量。单价差超过 15% 则不用。"""
    if quantity <= 0:
        raise ClearanceError("数量必须为正")
    best: Optional[Tuple[int, int]] = None
    for price, qty in samples:
        if type(price) is not int or type(qty) is not int or price <= 0 or qty <= 0:
            continue
        unit = price // qty
        distance = abs(unit * quantity - price)
        if best is None or distance < best[0]:
            best = (distance, unit)
    if best is None:
        return None
    reference = best[1] * quantity
    if abs(best[1] * quantity - reference) > reference * 15 // 100:
        return None
    return best[1] * quantity


def deductive_value(resale_cents: int, profit_cents: int, inland_cents: int) -> int:
    """倒扣价格法：国内转售价减去利润和内陆费用。"""
    if min(resale_cents, profit_cents, inland_cents) < 0:
        raise ClearanceError("倒扣项目不能为负")
    value = resale_cents - profit_cents - inland_cents
    if value <= 0:
        raise ClearanceError("倒扣后完税价格不是正数")
    return value


def computed_value(material_cents: int, labor_cents: int, profit_cents: int, packing_cents: int) -> int:
    """计算价格法：料工费加利润和包装。"""
    parts = (material_cents, labor_cents, profit_cents, packing_cents)
    if any(type(item) is not int or item < 0 for item in parts):
        raise ClearanceError("计算价格的项目不合法")
    return sum(parts)


def choose_value(
    method: str,
    invoice_cents: int,
    freight_cents: int,
    insurance_cents: int,
    identical: Sequence[int],
    similar: Sequence[Tuple[int, int]],
    quantity: int,
    resale_cents: int,
    profit_cents: int,
    inland_cents: int,
    material_cents: int,
    labor_cents: int,
    maker_profit_cents: int,
    packing_cents: int,
) -> Tuple[str, int]:
    """按申报的方法估价。该方法没有可用数字时，按成交、相同、类似、倒扣、计算的顺序换下一种。"""
    order = ["成交", "相同", "类似", "倒扣", "计算"]
    if method not in order:
        raise ClearanceError("估价方法不存在")
    start = order.index(method)
    for name in order[start:] + order[:start]:
        if name == "成交":
            return name, transaction_value(invoice_cents, freight_cents, insurance_cents)
        if name == "相同":
            found = identical_value(identical)
            if found is not None:
                return name, found
        elif name == "类似":
            found = similar_value(similar, quantity)
            if found is not None:
                return name, found
        elif name == "倒扣":
            try:
                return name, deductive_value(resale_cents, profit_cents, inland_cents)
            except ClearanceError:
                continue
        elif name == "计算":
            return name, computed_value(material_cents, labor_cents, maker_profit_cents, packing_cents)
    raise ClearanceError("没有可用的估价")


def duty_cents(customs_value: int, duty_permille: int, vat_permille: int, excise_permille: int) -> Dict[str, int]:
    """关税计税价格是完税价格。消费税从价。增值税的计税价格含关税和消费税。"""
    if customs_value < 0:
        raise ClearanceError("完税价格不能为负")
    duty = customs_value * duty_permille // 1000
    base_for_excise = customs_value + duty
    if excise_permille >= 1000:
        raise ClearanceError("消费税率不合法")
    # 从价消费税：税额 = 组成计税价格 * 税率，组成计税价格 = (完税价格 + 关税) / (1 - 税率)。
    if excise_permille == 0:
        excise = 0
    else:
        excise = base_for_excise * excise_permille // (1000 - excise_permille)
    vat_base = customs_value + duty + excise
    vat = vat_base * vat_permille // 1000
    return {"关税": duty, "消费税": excise, "增值税": vat, "合计": duty + excise + vat}


def late_penalty(tax_cents: int, late_hours: int) -> int:
    """滞纳从缴款期限届满的下一个小时起算，每 24 小时按税额的千分之五，不足 24 小时不计，上限是税额本身。"""
    if tax_cents < 0 or late_hours < 0:
        raise ClearanceError("滞纳参数不合法")
    days = late_hours // 24
    penalty = tax_cents * days * 5 // 1000
    if penalty > tax_cents:
        return tax_cents
    return penalty


def bond_cents(tax_cents: int, risk: str) -> int:
    factor = {"低": 0, "中": 300, "高": 1000, "保税": 100}
    if risk not in factor:
        raise ClearanceError("风险等级不存在")
    return tax_cents * factor[risk] // 1000


def missing_documents(kind: str, presented: Sequence[str]) -> List[str]:
    if kind not in DOCUMENTS:
        raise ClearanceError("货物类别不存在")
    have = {item.strip() for item in presented}
    return [item for item in DOCUMENTS[kind] if item not in have]


def missing_permits(hs_code: str, presented: Sequence[str]) -> List[str]:
    _duty, _vat, _excise, permits = lookup_hs(hs_code)
    have = {item.strip() for item in presented}
    return [item for item in permits if item not in have]


class Declaration:
    """一份报关单。状态只能沿 TRANSITIONS 走。"""

    def __init__(self, entry_id: str, hs_code: str, kind: str, quantity: int) -> None:
        if quantity <= 0:
            raise ClearanceError("数量必须为正")
        lookup_hs(hs_code)
        if kind not in DOCUMENTS:
            raise ClearanceError("货物类别不存在")
        self.entry_id = entry_id.strip()
        self.hs_code = hs_code.strip()
        self.kind = kind
        self.quantity = quantity
        self.state = "草稿"
        self.documents: List[str] = []
        self.permits: List[str] = []
        self.customs_value = 0
        self.method = ""
        self.tax: Dict[str, int] = {}
        self.paid = 0
        self.history: List[str] = ["草稿"]

    def attach(self, documents: Sequence[str], permits: Sequence[str]) -> None:
        if self.state not in ("草稿", "退单"):
            raise ClearanceError("当前状态不能补单证")
        self.documents = [item.strip() for item in documents if item.strip()]
        self.permits = [item.strip() for item in permits if item.strip()]

    def appraise(self, **kwargs: object) -> None:
        if self.state not in ("草稿", "退单"):
            raise ClearanceError("当前状态不能估价")
        method = str(kwargs.get("method", "成交"))
        name, value = choose_value(
            method,
            int(kwargs.get("invoice_cents", 0)),
            int(kwargs.get("freight_cents", 0)),
            int(kwargs.get("insurance_cents", 0)),
            tuple(kwargs.get("identical", ())),  # type: ignore[arg-type]
            tuple(kwargs.get("similar", ())),  # type: ignore[arg-type]
            self.quantity,
            int(kwargs.get("resale_cents", 0)),
            int(kwargs.get("profit_cents", 0)),
            int(kwargs.get("inland_cents", 0)),
            int(kwargs.get("material_cents", 0)),
            int(kwargs.get("labor_cents", 0)),
            int(kwargs.get("maker_profit_cents", 0)),
            int(kwargs.get("packing_cents", 0)),
        )
        duty, vat, excise, _permits = lookup_hs(self.hs_code)
        self.method = name
        self.customs_value = value
        self.tax = duty_cents(value, duty, vat, excise)

    def move(self, target: str) -> None:
        allowed = TRANSITIONS[self.state]
        if target not in allowed:
            raise ClearanceError("不能从{}到{}".format(self.state, target))
        if target == "已申报":
            missing = missing_documents(self.kind, self.documents)
            missing += missing_permits(self.hs_code, self.permits)
            if missing:
                raise ClearanceError("缺" + "、".join(missing))
            if self.customs_value <= 0:
                raise ClearanceError("还没有估价")
        if target == "已放行":
            if self.paid < self.tax.get("合计", 0):
                raise ClearanceError("税款未缴清")
        self.state = target
        self.history.append(target)

    def pay(self, cents: int) -> None:
        if self.state != "待缴税":
            raise ClearanceError("当前状态不能缴税")
        if type(cents) is not int or cents <= 0:
            raise ClearanceError("缴款必须是正整数分")
        self.paid += cents

    def outstanding(self, late_hours: int = 0) -> int:
        tax = self.tax.get("合计", 0)
        due = tax + late_penalty(tax, late_hours)
        remain = due - self.paid
        return remain if remain > 0 else 0
