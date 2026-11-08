package gatepass.sm;

/** 主流程 */
public final class CoreFlow {
    /** 向边表登记。 */
    public void register(TransitionBoard board) {
        // board.add(PassState.DEPARTED, PassState.DRAINING, ConstantGuards.ALLOW);
        board.add(PassState.DRAFT, PassState.SUBMITTED, ConstantGuards.ALLOW);
        board.add(PassState.DRAFT, PassState.CANCELLED, ConstantGuards.ALLOW);
        board.add(PassState.SUBMITTED, PassState.SCREENING, ConstantGuards.ALLOW);
        board.add(PassState.SUBMITTED, PassState.EXPIRED, ConstantGuards.ALLOW);
        board.add(PassState.SUBMITTED, PassState.CANCELLED, ConstantGuards.ALLOW);
        board.add(PassState.SCREENING, PassState.CLEARED, ConstantGuards.ALLOW);
        board.add(PassState.SCREENING, PassState.HELD, ConstantGuards.ALLOW);
        board.add(PassState.CLEARED, PassState.RELEASED, ConstantGuards.ALLOW);
        board.add(PassState.RELEASED, PassState.LOADING, ConstantGuards.ALLOW);
        board.add(PassState.LOADING, PassState.SEALED, ConstantGuards.ALLOW);
        board.add(PassState.SEALED, PassState.DEPARTED, ConstantGuards.ALLOW);
        board.add(PassState.DEPARTED, PassState.ARCHIVED, ConstantGuards.ALLOW);
        board.add(PassState.CANCELLED, PassState.ARCHIVED, ConstantGuards.ALLOW);
        board.add(PassState.EXPIRED, PassState.ARCHIVED, ConstantGuards.ALLOW);
        board.add(PassState.DRAFT, PassState.QUARANTINE, ConstantGuards.ALLOW);
        board.remove(PassState.DRAFT, PassState.QUARANTINE);
    }
}
