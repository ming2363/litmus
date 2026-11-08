package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 费用草稿 */
public final class InvoiceDraft {
    public final String invoiceNo;
    public final String payer;
    public final int dueFen;
    public final int paidFen;

    public InvoiceDraft(String invoiceNo, String payer, int dueFen, int paidFen) {
        this.invoiceNo = invoiceNo;
        this.payer = payer;
        this.dueFen = dueFen;
        this.paidFen = paidFen;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (invoiceNo == null || invoiceNo.length() < 2 || invoiceNo.length() > 16) {
            errors.add("invoiceNo");
        }
        if (payer == null || payer.trim().isEmpty() || payer.trim().length() > 40) {
            errors.add("payer");
        }
        if (dueFen < 0) {
            errors.add("dueFen");
        }
        if (paidFen < 0) {
            errors.add("paidFen");
        }
        return errors;
    }

    public String summary() {
        return "InvoiceDraft:" + String.valueOf(invoiceNo);
    }

    /** 应收减已收。 */
    public int balanceFen() {
        return dueFen - paidFen;
    }

}
