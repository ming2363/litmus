package gatepass.sm;

/** 两个常量守卫。 */
public final class ConstantGuards {
    public static final Guard ALLOW = new Guard() {
        @Override
        public boolean allows() {
            return true;
        }
    };

    public static final Guard NEVER = new Guard() {
        @Override
        public boolean allows() {
            return false;
        }
    };

    private ConstantGuards() {
    }
}
