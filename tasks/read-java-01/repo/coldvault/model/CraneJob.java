package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 门机作业 */
public final class CraneJob {
    public final String jobNo;
    public final String crane;
    public final String status;
    public final int moves;

    public CraneJob(String jobNo, String crane, String status, int moves) {
        this.jobNo = jobNo;
        this.crane = crane;
        this.status = status;
        this.moves = moves;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (jobNo == null || jobNo.length() < 2 || jobNo.length() > 16) {
            errors.add("jobNo");
        }
        if (crane == null || crane.trim().isEmpty() || crane.trim().length() > 40) {
            errors.add("crane");
        }
        if (!("queued".equals(status) || "assigned".equals(status) || "working".equals(status) || "done".equals(status))) {
            errors.add("status");
        }
        if (moves < 0 || moves > 800) {
            errors.add("moves");
        }
        return errors;
    }

    public String summary() {
        return "CraneJob:" + String.valueOf(jobNo);
    }

    /** 已派工或作业中。 */
    public boolean busy() {
        return "assigned".equals(status) || "working".equals(status);
    }

}
