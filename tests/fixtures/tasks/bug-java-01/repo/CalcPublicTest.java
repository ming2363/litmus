public class CalcPublicTest {
    public void testAdd() {
        if (Calc.add(1, 2) != 3) {
            throw new AssertionError("add failed");
        }
    }
}
