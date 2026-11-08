package berthroster.support;

/** 以分为单位的金额工具。 */
public final class Money {
    private Money() {
    }

    /** 把元文本解析成分。最多两位小数。 */
    public static int parseFen(String text) {
        if (text == null) {
            throw new IllegalArgumentException("text");
        }
        String raw = text.trim();
        int sign = 1;
        if (raw.startsWith("-")) {
            sign = -1;
            raw = raw.substring(1);
        }
        int dot = raw.indexOf('.');
        String whole = dot < 0 ? raw : raw.substring(0, dot);
        String frac = dot < 0 ? "" : raw.substring(dot + 1);
        if (whole.isEmpty() || !allDigits(whole) || frac.length() > 2 || !allDigits(frac)) {
            throw new IllegalArgumentException(text);
        }
        if (raw.indexOf('.', dot + 1) >= 0) {
            throw new IllegalArgumentException(text);
        }
        while (frac.length() < 2) {
            frac = frac + "0";
        }
        return sign * (Integer.parseInt(whole) * 100 + Integer.parseInt(frac));
    }

    /** 分格式化为两位小数的元。 */
    public static String formatFen(int amount) {
        String sign = amount < 0 ? "-" : "";
        int value = Math.abs(amount);
        return sign + (value / 100) + "." + pad2(value % 100);
    }

    /** 按权重分配，余数给当前余数最大的下标。 */
    public static int[] allocate(int total, int[] weights) {
        if (weights == null || weights.length == 0) {
            throw new IllegalArgumentException("weights");
        }
        int base = 0;
        for (int i = 0; i < weights.length; i++) {
            if (weights[i] < 0) {
                throw new IllegalArgumentException("weights");
            }
            base += weights[i];
        }
        int[] shares = new int[weights.length];
        if (base == 0) {
            if (total != 0) {
                throw new IllegalArgumentException("zero-weight");
            }
            return shares;
        }
        int[] raw = new int[weights.length];
        int used = 0;
        for (int i = 0; i < weights.length; i++) {
            raw[i] = total * weights[i];
            shares[i] = raw[i] / base;
            used += shares[i];
        }
        int remain = total - used;
        int step = remain > 0 ? 1 : -1;
        int left = Math.abs(remain);
        while (left > 0) {
            int pick = 0;
            for (int i = 1; i < weights.length; i++) {
                int leftMod = Math.abs(raw[pick] % base);
                int rightMod = Math.abs(raw[i] % base);
                if (rightMod > leftMod) {
                    pick = i;
                }
            }
            shares[pick] += step;
            raw[pick] -= step * base;
            left -= 1;
        }
        return shares;
    }

    /** 超额累进。capsFen 与 ratesPerMille 等长，最后一档上限用 Integer.MAX_VALUE。 */
    public static int tierTax(int amountFen, int[] capsFen, int[] ratesPerMille) {
        if (amountFen < 0 || capsFen.length != ratesPerMille.length) {
            throw new IllegalArgumentException("tax");
        }
        int tax = 0;
        int previous = 0;
        for (int i = 0; i < capsFen.length; i++) {
            int cap = capsFen[i];
            int span = Math.min(amountFen, cap) - previous;
            if (span > 0) {
                tax += span * ratesPerMille[i] / 1000;
            }
            if (amountFen <= cap) {
                break;
            }
            previous = cap;
        }
        return tax;
    }

    public static int clampFee(int amount, int floor, int ceiling) {
        if (floor > ceiling) {
            throw new IllegalArgumentException("range");
        }
        if (amount < floor) {
            return floor;
        }
        if (amount > ceiling) {
            return ceiling;
        }
        return amount;
    }

    private static boolean allDigits(String text) {
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            if (ch < '0' || ch > '9') {
                return false;
            }
        }
        return true;
    }

    private static String pad2(int value) {
        if (value < 10) {
            return "0" + value;
        }
        return Integer.toString(value);
    }
}
