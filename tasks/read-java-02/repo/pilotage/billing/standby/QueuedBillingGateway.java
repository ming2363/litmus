package pilotage.billing.standby;

import pilotage.billing.BillingGateway;

/** 备用队列计费 */
public final class QueuedBillingGateway implements BillingGateway {
    @Override
    public int quoteFen(String voyageNo) {
        if (voyageNo == null || voyageNo.isEmpty()) {
            return 0;
        }
        return voyageNo.length() * 100;
    }
}
