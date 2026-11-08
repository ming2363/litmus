"""模型目录，供报表枚举类型名。"""

MODEL_NAMES = (
    "BerthCard",
    "VoyageCall",
    "TideWindow",
    "PilotOrder",
    "CargoHold",
    "WorkerShift",
    "GateTicket",
    "ColdProbe",
    "InvoiceDraft",
    "DemurrageSlip",
    "BadgePass",
    "YardSlot",
    "CraneJob",
    "BargePlan",
    "NightVoucher",
    "WeatherHold",
    "ChannelDraft",
    "MooringLine",
    "FuelIssue",
    "WasteReceipt",
    "RadioLog",
    "SafetyDrill",
    "CustomsSeal",
    "WaterSupply",
)


def model_count():
    """领域类型数量。"""
    return len(MODEL_NAMES)

