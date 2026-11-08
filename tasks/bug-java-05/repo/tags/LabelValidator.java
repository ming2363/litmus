package tags;

import java.util.regex.Pattern;

/**
 * 用嵌套量词检查点分标签。接近匹配的长串会把引擎拖进大量回溯。
 */
public final class LabelValidator {

    public static final int MAX_LABEL = 48;
    public static final int MAX_TOTAL = 96;

    private static final Pattern PATTERN = Pattern.compile("^(([a-z0-9]+)+\\.)*[a-z0-9]+$");

    private LabelValidator() {
    }

    public static boolean isValid(String label) {
        if (label == null) {
            throw new NullPointerException("label");
        }
        if (label.isEmpty() || label.length() > MAX_TOTAL) {
            return false;
        }
        return PATTERN.matcher(label).matches();
    }
}
