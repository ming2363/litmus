package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 燃油加注 */
public final class FuelIssue {
    public final String issueNo;
    public final int issuedL;
    public final int usedL;
    public final String grade;

    public FuelIssue(String issueNo, int issuedL, int usedL, String grade) {
        this.issueNo = issueNo;
        this.issuedL = issuedL;
        this.usedL = usedL;
        this.grade = grade;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (issueNo == null || issueNo.length() < 2 || issueNo.length() > 16) {
            errors.add("issueNo");
        }
        if (issuedL < 0 || issuedL > 500000) {
            errors.add("issuedL");
        }
        if (usedL < 0 || usedL > 500000) {
            errors.add("usedL");
        }
        if (grade == null || grade.trim().isEmpty() || grade.trim().length() > 40) {
            errors.add("grade");
        }
        return errors;
    }

    public String summary() {
        return "FuelIssue:" + String.valueOf(issueNo);
    }

    /** 剩余升数不为负。 */
    public int leftoverLitre() {
        int left = issuedL - usedL;
        if (left < 0) {
            return 0;
        }
        return left;
    }

}
