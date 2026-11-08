package gatepass.sm;

/** 排空流程 */
public final class DrainFlow {
    /** 向边表登记。 */
    public void register(TransitionBoard board) {
        board.add(PassState.CLEARED, PassState.DRAINING, ConstantGuards.NEVER);
        board.add(PassState.DRAINING, PassState.ARCHIVED, ConstantGuards.ALLOW);
    }
}
