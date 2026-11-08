package yardorder.support;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** KEY=VALUE 行协议。 */
public final class ManifestDoc {
    private ManifestDoc() {
    }

    public static List<String[]> parse(String text) {
        Map<String, String> values = new LinkedHashMap<String, String>();
        String[] lines = text.split("\n", -1);
        for (int i = 0; i < lines.length; i++) {
            String line = lines[i].trim();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            int eq = line.indexOf('=');
            if (eq <= 0) {
                throw new IllegalArgumentException("line " + (i + 1));
            }
            String key = line.substring(0, eq).trim();
            String value = line.substring(eq + 1).trim();
            values.put(key, value);
        }
        List<String[]> pairs = new ArrayList<String[]>();
        for (Map.Entry<String, String> entry : values.entrySet()) {
            pairs.add(new String[] {entry.getKey(), entry.getValue()});
        }
        return pairs;
    }

    public static String require(List<String[]> pairs, String key) {
        for (int i = 0; i < pairs.size(); i++) {
            if (key.equals(pairs.get(i)[0])) {
                return pairs.get(i)[1];
            }
        }
        throw new IllegalArgumentException(key);
    }
}
