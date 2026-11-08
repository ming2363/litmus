package holdledger.flow;

import holdledger.error.LedgerIOException;
import holdledger.error.StaleReservationException;
import holdledger.reserve.GenerationGuard;

/** 单笔确认流程。只捕获读写异常，过期异常继续往外抛。 */
public final class ConfirmFlow {
    private final GenerationGuard guard;

    public ConfirmFlow(GenerationGuard guard) {
        this.guard = guard;
    }

    public String run(String holdId, long generation) throws StaleReservationException {
        try {
            guard.checkThen(holdId, generation);
            noteIO();
        } catch (LedgerIOException ex) {
            return "io";
        }
        return "ok";
    }

    private void noteIO() throws LedgerIOException {
        // 读写钩子。当前实现不抛。
    }
}
