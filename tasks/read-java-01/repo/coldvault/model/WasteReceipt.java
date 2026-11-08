package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 污染物接收 */
public final class WasteReceipt {
    public final String receiptNo;
    public final int kg;
    public final int freeKg;
    public final String kind;

    public WasteReceipt(String receiptNo, int kg, int freeKg, String kind) {
        this.receiptNo = receiptNo;
        this.kg = kg;
        this.freeKg = freeKg;
        this.kind = kind;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (receiptNo == null || receiptNo.length() < 2 || receiptNo.length() > 16) {
            errors.add("receiptNo");
        }
        if (kg < 0 || kg > 50000) {
            errors.add("kg");
        }
        if (freeKg < 0 || freeKg > 1000) {
            errors.add("freeKg");
        }
        if (!("oil".equals(kind) || "garbage".equals(kind) || "sewage".equals(kind))) {
            errors.add("kind");
        }
        return errors;
    }

    public String summary() {
        return "WasteReceipt:" + String.valueOf(receiptNo);
    }

    /** 超过免登记公斤数。 */
    public boolean needsReceipt() {
        return kg > freeKg;
    }

}
