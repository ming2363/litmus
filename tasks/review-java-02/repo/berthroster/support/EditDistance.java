package berthroster.support;

/** 编辑距离。 */
public final class EditDistance {
    private EditDistance() {
    }

    public static int distance(String left, String right) {
        if (left == null || right == null) {
            throw new IllegalArgumentException("text");
        }
        int n = left.length();
        int m = right.length();
        int[] prev = new int[m + 1];
        for (int j = 0; j <= m; j++) {
            prev[j] = j;
        }
        for (int i = 1; i <= n; i++) {
            int[] curr = new int[m + 1];
            curr[0] = i;
            for (int j = 1; j <= m; j++) {
                int cost = left.charAt(i - 1) == right.charAt(j - 1) ? 0 : 1;
                curr[j] = Math.min(Math.min(prev[j] + 1, curr[j - 1] + 1), prev[j - 1] + cost);
            }
            prev = curr;
        }
        return prev[m];
    }
}
