package gatepass.sm;

/** 查验流程 */
public final class InspectionFlow {
    /** 向边表登记。 */
    public void register(TransitionBoard board) {
        board.add(PassState.HELD, PassState.INSPECTION, ConstantGuards.ALLOW);
        board.add(PassState.INSPECTION, PassState.CLEARED, ConstantGuards.ALLOW);
        board.add(PassState.INSPECTION, PassState.CANCELLED, ConstantGuards.ALLOW);
    }
}
