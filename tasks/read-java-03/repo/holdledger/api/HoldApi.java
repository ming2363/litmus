package holdledger.api;

import holdledger.error.StaleReservationException;
import holdledger.flow.ConfirmFlow;

/** 预占接口。 */
public final class HoldApi {
    private final ConfirmFlow flow;

    public HoldApi(ConfirmFlow flow) {
        this.flow = flow;
    }

    /** 单笔确认。过期时在本方法收口。 */
    public String confirmHold(String holdId, long generation) {
        try {
            return flow.run(holdId, generation);
        } catch (IllegalArgumentException ex) {
            return "bad-request";
        } catch (StaleReservationException ex) {
            return "conflict";
        }
    }
}
