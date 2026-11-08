package holdledger.error;

/** 预占代数已经变化。受检异常。 */
public class StaleReservationException extends Exception {
    private final String holdId;

    public StaleReservationException(String holdId) {
        super(holdId);
        this.holdId = holdId;
    }

    public String getHoldId() {
        return holdId;
    }
}
