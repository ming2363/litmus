public class Calc {
    public static int add(int a, int b) {
        return a + b;
    }

    public static long absDiff(int a, int b) {
        // 缺陷：int 相减会溢出
        return Math.abs(a - b);
    }
}
