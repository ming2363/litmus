package holdledger.job;

/** 导入任务会吞掉更宽的异常，但确认链不经过这里。 */
public final class SnapshotImport {
    public String load(String text) {
        try {
            if (text == null) {
                throw new IllegalStateException("empty");
            }
            return text.trim();
        } catch (Exception ex) {
            return "failed";
        }
    }
}
