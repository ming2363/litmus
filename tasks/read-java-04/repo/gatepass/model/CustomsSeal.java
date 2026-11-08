package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 海关封志 */
public final class CustomsSeal {
    public final String sealNo;
    public final String boxNo;
    public final boolean broken;

    public CustomsSeal(String sealNo, String boxNo, boolean broken) {
        this.sealNo = sealNo;
        this.boxNo = boxNo;
        this.broken = broken;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (sealNo == null || sealNo.length() < 2 || sealNo.length() > 16) {
            errors.add("sealNo");
        }
        if (boxNo == null || boxNo.trim().isEmpty() || boxNo.trim().length() > 40) {
            errors.add("boxNo");
        }

        return errors;
    }

    public String summary() {
        return "CustomsSeal:" + String.valueOf(sealNo);
    }

    /** 有封志号且未拆。 */
    public boolean intact() {
        return sealNo != null && !sealNo.isEmpty() && !broken;
    }

}
