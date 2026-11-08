package hitcount;

import java.util.Map;

/**
 * 把计数快照渲染成稳定的多行文本。
 */
public final class HitReport {

    private HitReport() {
    }

    public static String render(HitCounter counter) {
        if (counter == null) {
            throw new NullPointerException("counter");
        }
        StringBuilder builder = new StringBuilder();
        for (Map.Entry<String, Long> entry : counter.snapshot().entrySet()) {
            builder.append(entry.getKey()).append('=').append(entry.getValue()).append('\n');
        }
        return builder.toString();
    }
}
