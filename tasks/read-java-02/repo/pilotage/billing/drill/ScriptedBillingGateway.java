package pilotage.billing.drill;

import pilotage.billing.BillingGateway;

/** 演练脚本计费 */
public final class ScriptedBillingGateway implements BillingGateway {
    @Override
    public int quoteFen(String voyageNo) {
        if (voyageNo == null || voyageNo.isEmpty()) {
            return 0;
        }
        return voyageNo.length() * 100;
    }
}
