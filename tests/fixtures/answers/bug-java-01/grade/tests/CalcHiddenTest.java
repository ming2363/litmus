public class CalcHiddenTest {
    public void testNormal() {
        if (Calc.absDiff(10, 3) != 7L) {
            throw new AssertionError("normal failed");
        }
    }

    public void testOverflow() {
        long got = Calc.absDiff(Integer.MAX_VALUE, Integer.MIN_VALUE);
        if (got != 4294967295L) {
            throw new AssertionError("overflow failed: " + got);
        }
    }
}
