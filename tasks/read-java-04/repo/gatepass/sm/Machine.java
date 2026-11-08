package gatepass.sm;

/** 把登记器装到一张边表上。 */
public final class Machine {
    private final TransitionBoard board;

    public Machine(TransitionBoard board) {
        this.board = board;
    }

    /** 按固定顺序登记。缺失的外部时钟不改变边。 */
    public static Machine build() {
        TransitionBoard board = new TransitionBoard();
        new CoreFlow().register(board);
        new InspectionFlow().register(board);
        if (Flags.LEGACY_APPEAL) {
            new AppealFlow().register(board);
        }
        new QuarantineFlow().register(board);
        new DrainFlow().register(board);
        gatepass.external.TideClock.touch();
        return new Machine(board);
    }
}
