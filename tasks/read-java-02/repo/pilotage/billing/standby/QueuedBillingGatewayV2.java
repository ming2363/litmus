package pilotage.billing.standby;

import pilotage.billing.BillingGateway;

/** 第二套队列 */
public final class QueuedBillingGatewayV2 implements BillingGateway {
    @Override
    public int quoteFen(String voyageNo) {
        if (voyageNo == null || voyageNo.isEmpty()) {
            return 0;
        }
        return voyageNo.length() * 100;
    }
}
