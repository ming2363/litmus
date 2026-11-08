package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 驳船计划 */
public final class BargePlan {
    public final String bargeNo;
    public final String status;
    public final int tonnes;

    public BargePlan(String bargeNo, String status, int tonnes) {
        this.bargeNo = bargeNo;
        this.status = status;
        this.tonnes = tonnes;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (bargeNo == null || bargeNo.length() < 2 || bargeNo.length() > 16) {
            errors.add("bargeNo");
        }
        if (!("anchor".equals(status) || "in".equals(status) || "out".equals(status))) {
            errors.add("status");
        }
        if (tonnes < 0 || tonnes > 8000) {
            errors.add("tonnes");
        }
        return errors;
    }

    public String summary() {
        return "BargePlan:" + String.valueOf(bargeNo);
    }

    /** 仍在锚地。 */
    public boolean waiting() {
        return "anchor".equals(status);
    }

}
