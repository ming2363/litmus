package holdledger.api;

import holdledger.error.StaleReservationException;
import holdledger.reserve.ReservationBook;

/** 批量重放。捕获点不在单笔确认链上。 */
public final class BatchApi {
    private final ReservationBook book;

    public BatchApi(ReservationBook book) {
        this.book = book;
    }

    public String replayHold(String holdId, long generation) {
        try {
            book.replay(holdId, generation);
            return "ok";
        } catch (StaleReservationException ex) {
            return "conflict";
        }
    }
}
