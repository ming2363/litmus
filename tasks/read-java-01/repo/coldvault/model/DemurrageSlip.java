package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 滞期草稿 */
public final class DemurrageSlip {
    public final String slipNo;
    public final int minutes;
    public final int capMin;
    public final String reason;

    public DemurrageSlip(String slipNo, int minutes, int capMin, String reason) {
        this.slipNo = slipNo;
        this.minutes = minutes;
        this.capMin = capMin;
        this.reason = reason;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (slipNo == null || slipNo.length() < 2 || slipNo.length() > 16) {
            errors.add("slipNo");
        }
        if (minutes < 0 || minutes > 20000) {
            errors.add("minutes");
        }
        if (capMin < 1 || capMin > 20000) {
            errors.add("capMin");
        }
        if (reason == null || reason.trim().isEmpty() || reason.trim().length() > 40) {
            errors.add("reason");
        }
        return errors;
    }

    public String summary() {
        return "DemurrageSlip:" + String.valueOf(slipNo);
    }

    /** 不超过封顶分钟。 */
    public int cappedMinutes() {
        if (minutes > capMin) {
            return capMin;
        }
        return minutes;
    }

}
