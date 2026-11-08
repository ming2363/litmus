package pilotage.model;

import java.util.ArrayList;
import java.util.List;

/** 引航委托 */
public final class PilotOrder {
    public final String orderNo;
    public final int minutes;
    public final int minimumMin;
    public final String side;

    public PilotOrder(String orderNo, int minutes, int minimumMin, String side) {
        this.orderNo = orderNo;
        this.minutes = minutes;
        this.minimumMin = minimumMin;
        this.side = side;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (orderNo == null || orderNo.length() < 2 || orderNo.length() > 16) {
            errors.add("orderNo");
        }
        if (minutes < 0 || minutes > 600) {
            errors.add("minutes");
        }
        if (minimumMin < 30 || minimumMin > 180) {
            errors.add("minimumMin");
        }
        if (!("port".equals(side) || "starboard".equals(side) || "either".equals(side))) {
            errors.add("side");
        }
        return errors;
    }

    public String summary() {
        return "PilotOrder:" + String.valueOf(orderNo);
    }

    /** 不足起步分钟按起步计。 */
    public int billableMinutes() {
        if (minutes < minimumMin) {
            return minimumMin;
        }
        return minutes;
    }

}
