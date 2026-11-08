package gatepass.sm;

/** 隔离流程 */
public final class QuarantineFlow {
    /** 向边表登记。 */
    public void register(TransitionBoard board) {
        board.add(PassState.QUARANTINE, PassState.INSPECTION, ConstantGuards.ALLOW);
    }
}
