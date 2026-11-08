package pilotage.model;

import java.util.ArrayList;
import java.util.List;

/** 堆场箱位 */
public final class YardSlot {
    public final String slotNo;
    public final int lengthM;
    public final String status;
    public final int tier;

    public YardSlot(String slotNo, int lengthM, String status, int tier) {
        this.slotNo = slotNo;
        this.lengthM = lengthM;
        this.status = status;
        this.tier = tier;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (slotNo == null || slotNo.length() < 2 || slotNo.length() > 16) {
            errors.add("slotNo");
        }
        if (lengthM < 3 || lengthM > 20) {
            errors.add("lengthM");
        }
        if (!("empty".equals(status) || "occupied".equals(status) || "locked".equals(status))) {
            errors.add("status");
        }
        if (tier < 1 || tier > 6) {
            errors.add("tier");
        }
        return errors;
    }

    public String summary() {
        return "YardSlot:" + String.valueOf(slotNo);
    }

    /** 空闲且长度够。 */
    public boolean fits(int needLength) {
        return "empty".equals(status) && needLength <= lengthM;
    }

}
