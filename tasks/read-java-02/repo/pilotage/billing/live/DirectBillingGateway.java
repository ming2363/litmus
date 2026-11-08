package pilotage.billing.live;

import pilotage.billing.BillingGateway;

/** 现场直接计费 */
public final class DirectBillingGateway implements BillingGateway {
    @Override
    public int quoteFen(String voyageNo) {
        if (voyageNo == null || voyageNo.isEmpty()) {
            return 0;
        }
        return voyageNo.length() * 100;
    }
}
