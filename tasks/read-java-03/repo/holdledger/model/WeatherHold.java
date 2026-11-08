package holdledger.model;

import java.util.ArrayList;
import java.util.List;

/** 气象管制 */
public final class WeatherHold {
    public final String noticeNo;
    public final String level;
    public final int hours;

    public WeatherHold(String noticeNo, String level, int hours) {
        this.noticeNo = noticeNo;
        this.level = level;
        this.hours = hours;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (noticeNo == null || noticeNo.length() < 2 || noticeNo.length() > 16) {
            errors.add("noticeNo");
        }
        if (!("watch".equals(level) || "stop_sail".equals(level) || "stop_lift".equals(level) || "clear".equals(level))) {
            errors.add("level");
        }
        if (hours < 0 || hours > 72) {
            errors.add("hours");
        }
        return errors;
    }

    public String summary() {
        return "WeatherHold:" + String.valueOf(noticeNo);
    }

    /** 禁航或禁吊。 */
    public boolean blocking() {
        return "stop_sail".equals(level) || "stop_lift".equals(level);
    }

}
