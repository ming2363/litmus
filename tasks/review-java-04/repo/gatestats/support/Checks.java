package gatestats.support;

/** 数字校验码。 */
public final class Checks {
    private Checks() {
    }

    public static boolean luhnOk(String number) {
        if (number == null || number.length() < 2) {
            return false;
        }
        int total = 0;
        for (int i = 0; i < number.length(); i++) {
            char ch = number.charAt(number.length() - 1 - i);
            if (ch < '0' || ch > '9') {
                return false;
            }
            int digit = ch - '0';
            if (i % 2 == 1) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            total += digit;
        }
        return total % 10 == 0;
    }

    public static char mod11Symbol(String body) {
        if (body == null || body.isEmpty()) {
            throw new IllegalArgumentException("body");
        }
        int total = 0;
        int weight = 2;
        for (int i = body.length() - 1; i >= 0; i--) {
            char ch = body.charAt(i);
            if (ch < '0' || ch > '9') {
                throw new IllegalArgumentException(body);
            }
            total += (ch - '0') * weight;
            weight += 1;
            if (weight > 7) {
                weight = 2;
            }
        }
        int mod = total % 11;
        if (mod == 10) {
            return 'X';
        }
        return (char) ('0' + mod);
    }
}
