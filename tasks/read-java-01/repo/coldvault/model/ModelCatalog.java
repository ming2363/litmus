package coldvault.model;

/** 领域类型目录。 */
public final class ModelCatalog {
    private ModelCatalog() {
    }

    public static String[] names() {
        return new String[] {
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
        "WaterSupply"
        };
    }

    public static int modelCount() {
        return names().length;
    }
}
