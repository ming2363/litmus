package holdledger.model;

import java.util.ArrayList;
import java.util.List;

/** 温度探针 */
public final class ColdProbe {
    public final String probeNo;
    public final int seenMin;
    public final int celsius;
    public final String zone;

    public ColdProbe(String probeNo, int seenMin, int celsius, String zone) {
        this.probeNo = probeNo;
        this.seenMin = seenMin;
        this.celsius = celsius;
        this.zone = zone;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (probeNo == null || probeNo.length() < 2 || probeNo.length() > 16) {
            errors.add("probeNo");
        }
        if (seenMin < 0 || seenMin > 200000) {
            errors.add("seenMin");
        }
        if (celsius < -40 || celsius > 40) {
            errors.add("celsius");
        }
        if (zone == null || zone.trim().isEmpty() || zone.trim().length() > 40) {
            errors.add("zone");
        }
        return errors;
    }

    public String summary() {
        return "ColdProbe:" + String.valueOf(probeNo);
    }

    /** 采样间隔超过阈值。 */
    public boolean stale(int nowMin, int limitMin) {
        return nowMin - seenMin > limitMin;
    }

}
