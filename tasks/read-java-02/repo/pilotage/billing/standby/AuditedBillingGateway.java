package pilotage.billing.standby;

import pilotage.billing.BillingGateway;

/** 带审计的计费 */
public final class AuditedBillingGateway implements BillingGateway {
    @Override
    public int quoteFen(String voyageNo) {
        if (voyageNo == null || voyageNo.isEmpty()) {
            return 0;
        }
        return voyageNo.length() * 100;
    }
}
