package holdledger.model;

import java.util.ArrayList;
import java.util.List;

/** 安全演习 */
public final class SafetyDrill {
    public final String drillNo;
    public final int present;
    public final int required;
    public final int openItems;

    public SafetyDrill(String drillNo, int present, int required, int openItems) {
        this.drillNo = drillNo;
        this.present = present;
        this.required = required;
        this.openItems = openItems;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (drillNo == null || drillNo.length() < 2 || drillNo.length() > 16) {
            errors.add("drillNo");
        }
        if (present < 0 || present > 500) {
            errors.add("present");
        }
        if (required < 1 || required > 500) {
            errors.add("required");
        }
        if (openItems < 0 || openItems > 50) {
            errors.add("openItems");
        }
        return errors;
    }

    public String summary() {
        return "SafetyDrill:" + String.valueOf(drillNo);
    }

    /** 人数够且没有未关闭项。 */
    public boolean passed() {
        return present >= required && openItems == 0;
    }

}
