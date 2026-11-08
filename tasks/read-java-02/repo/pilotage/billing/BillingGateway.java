package pilotage.billing;

/** 引航计费出口。 */
public interface BillingGateway {
    /** 返回本次计费的分。 */
    int quoteFen(String voyageNo);
}
