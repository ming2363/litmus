package holdledger.reserve;

import holdledger.error.StaleReservationException;

/** 确认前的代数门。本类不捕获过期异常。 */
public final class GenerationGuard {
    private final ReservationBook book;

    public GenerationGuard(ReservationBook book) {
        this.book = book;
    }

    public void checkThen(String holdId, long generation) throws StaleReservationException {
        book.confirm(holdId, generation);
    }
}
