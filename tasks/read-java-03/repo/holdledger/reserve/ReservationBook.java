package holdledger.reserve;

import holdledger.error.StaleReservationException;

/** 预占底账。 */
public final class ReservationBook {
    private final long storedGeneration;

    public ReservationBook(long storedGeneration) {
        this.storedGeneration = storedGeneration;
    }

    /** 代数不一致时抛出过期异常。 */
    public void confirm(String holdId, long generation) throws StaleReservationException {
        if (holdId == null || holdId.isEmpty()) {
            throw new IllegalArgumentException("holdId");
        }
        if (storedGeneration != generation) {
            throw new StaleReservationException(holdId);
        }
    }

    /** 重放走另一条方法，供批量接口使用。 */
    public void replay(String holdId, long generation) throws StaleReservationException {
        if (storedGeneration != generation) {
            throw new StaleReservationException(holdId);
        }
    }
}
