package berthroster.support;

/** 车牌与箱号的形状检查。 */
public final class PlateShape {
    private PlateShape() {
    }

    public static String normalize(String text) {
        if (text == null) {
            throw new IllegalArgumentException("plate");
        }
        StringBuilder buf = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            if (!Character.isWhitespace(ch)) {
                buf.append(Character.toUpperCase(ch));
            }
        }
        return buf.toString();
    }

    public static boolean containerOk(String text) {
        String raw = normalize(text);
        if (raw.length() != 11) {
            return false;
        }
        for (int i = 0; i < 4; i++) {
            if (!Character.isLetter(raw.charAt(i))) {
                return false;
            }
        }
        for (int i = 4; i < 11; i++) {
            if (!Character.isDigit(raw.charAt(i))) {
                return false;
            }
        }
        return true;
    }
}
