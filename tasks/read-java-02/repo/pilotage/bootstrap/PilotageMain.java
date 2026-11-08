package pilotage.bootstrap;

import java.io.IOException;

import pilotage.container.Selector;

/** 装配入口。外部时钟类不在本仓库。 */
public final class PilotageMain {
    private PilotageMain() {
    }

    public static int standbyQuoteFen() throws IOException {
        return Selector.choose("harbor-standby", "pilotage.billing.BillingGateway");
    }
}
