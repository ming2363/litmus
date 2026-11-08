package sliparchive;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

/** 读取票据模板。 */
public final class TemplateStore {
    /** 新的直读方法，给导出使用。 */
    public String readTemplate(Path path) throws IOException {
        FileInputStream in = new FileInputStream(path.toFile());
        byte[] buf = in.readAllBytes();
        return new String(buf, StandardCharsets.UTF_8);
    }

    /** 同一类里已经有会关闭流的读法。 */
    public String readTemplateSafe(Path path) throws IOException {
        try (InputStream in = new FileInputStream(path.toFile())) {
            byte[] buf = in.readAllBytes();
            return new String(buf, StandardCharsets.UTF_8);
        }
    }
}
