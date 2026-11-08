package pilotage.container;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 只读取 pilotage/config/<profile>.properties。 */
public final class Props {
    private Props() {
    }

    public static Map<String, String> load(String profile) throws IOException {
        Path path = Paths.get("pilotage", "config", profile + ".properties");
        Map<String, String> values = new HashMap<String, String>();
        if (!Files.isRegularFile(path)) {
            return values;
        }
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i).trim();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            int eq = line.indexOf('=');
            if (eq <= 0) {
                continue;
            }
            values.put(line.substring(0, eq).trim(), line.substring(eq + 1).trim());
        }
        return values;
    }
}
