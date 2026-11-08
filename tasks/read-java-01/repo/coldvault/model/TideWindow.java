package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 潮汐窗口 */
public final class TideWindow {
    public final String code;
    public final int startMin;
    public final int endMin;
    public final int heightCm;

    public TideWindow(String code, int startMin, int endMin, int heightCm) {
        this.code = code;
        this.startMin = startMin;
        this.endMin = endMin;
        this.heightCm = heightCm;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (code == null || code.length() < 2 || code.length() > 16) {
            errors.add("code");
        }
        if (startMin < 0 || startMin > 1440) {
            errors.add("startMin");
        }
        if (endMin < 0 || endMin > 2880) {
            errors.add("endMin");
        }
        if (heightCm < 0 || heightCm > 900) {
            errors.add("heightCm");
        }
        return errors;
    }

    public String summary() {
        return "TideWindow:" + String.valueOf(code);
    }

    /** 分钟落在半开窗口。 */
    public boolean containsMinute(int minute) {
        return startMin <= minute && minute < endMin;
    }

}
