package sliparchive;

/** 模板文件名。 */
public final class SlipName {
    private SlipName() {
    }

    public static String fileName(String code) {
        if (code == null || code.isEmpty()) {
            throw new IllegalArgumentException("code");
        }
        return "slip-" + code + ".txt";
    }
}
