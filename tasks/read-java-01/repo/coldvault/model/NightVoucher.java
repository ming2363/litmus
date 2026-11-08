package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 夜班凭证 */
public final class NightVoucher {
    public final String voucherNo;
    public final int debitFen;
    public final int creditFen;
    public final String desk;

    public NightVoucher(String voucherNo, int debitFen, int creditFen, String desk) {
        this.voucherNo = voucherNo;
        this.debitFen = debitFen;
        this.creditFen = creditFen;
        this.desk = desk;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (voucherNo == null || voucherNo.length() < 2 || voucherNo.length() > 16) {
            errors.add("voucherNo");
        }
        if (debitFen < 0) {
            errors.add("debitFen");
        }
        if (creditFen < 0) {
            errors.add("creditFen");
        }
        if (desk == null || desk.trim().isEmpty() || desk.trim().length() > 40) {
            errors.add("desk");
        }
        return errors;
    }

    public String summary() {
        return "NightVoucher:" + String.valueOf(voucherNo);
    }

    /** 借贷相等且非负。 */
    public boolean signed() {
        return debitFen >= 0 && debitFen == creditFen;
    }

}
