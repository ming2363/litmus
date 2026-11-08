package gatepass.sm;

/** 旧申诉流程 */
public final class AppealFlow {
    /** 向边表登记。 */
    public void register(TransitionBoard board) {
        board.add(PassState.HELD, PassState.APPEAL, ConstantGuards.ALLOW);
        board.add(PassState.APPEAL, PassState.APPEAL_OK, ConstantGuards.ALLOW);
        board.add(PassState.APPEAL, PassState.APPEAL_DENY, ConstantGuards.ALLOW);
        board.add(PassState.APPEAL_OK, PassState.RELEASED, ConstantGuards.ALLOW);
        board.add(PassState.SCREENING, PassState.QUARANTINE, ConstantGuards.ALLOW);
    }
}
