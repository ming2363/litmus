package pilotage.container;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** 全部环境的绑定。 */
public final class ProfileData {
    public static final List<Binding> BINDINGS = build();

    private ProfileData() {
    }

    private static List<Binding> build() {
        List<Binding> list = new ArrayList<Binding>();
        list.add(new Binding("harbor-live", "pilotage.billing.BillingGateway", "pilotage.billing.live.DirectBillingGateway", 10, null));
        list.add(new Binding("harbor-standby", "pilotage.billing.BillingGateway", "pilotage.billing.standby.AuditedBillingGateway", 5, "billing.audit.enabled"));
        list.add(new Binding("harbor-standby", "pilotage.billing.BillingGateway", "pilotage.billing.standby.QueuedBillingGatewayV2", 15, "billing.queue.v2"));
        list.add(new Binding("harbor-standby", "pilotage.billing.BillingGateway", "pilotage.billing.standby.QueuedBillingGateway", 20, null));
        list.add(new Binding("harbor-standby", "pilotage.billing.BillingGateway", "pilotage.billing.drill.ScriptedBillingGateway", 40, "billing.scripted"));
        list.add(new Binding("harbor-standby", "pilotage.billing.BillingGateway", "pilotage.billing.live.DirectBillingGateway", 1, "billing.force-direct"));
        list.add(new Binding("harbor-drill", "pilotage.billing.BillingGateway", "pilotage.billing.drill.ScriptedBillingGateway", 10, null));
        return Collections.unmodifiableList(list);
    }
}
