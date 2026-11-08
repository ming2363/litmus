package holdledger.model;

import java.util.ArrayList;
import java.util.List;

/** 工班时段 */
public final class WorkerShift {
    public final String workerNo;
    public final int startMin;
    public final int endMin;
    public final String role;

    public WorkerShift(String workerNo, int startMin, int endMin, String role) {
        this.workerNo = workerNo;
        this.startMin = startMin;
        this.endMin = endMin;
        this.role = role;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (workerNo == null || workerNo.length() < 2 || workerNo.length() > 16) {
            errors.add("workerNo");
        }
        if (startMin < 0 || startMin > 1440) {
            errors.add("startMin");
        }
        if (endMin < 0 || endMin > 1440) {
            errors.add("endMin");
        }
        if (!("signal".equals(role) || "tally".equals(role) || "driver".equals(role))) {
            errors.add("role");
        }
        return errors;
    }

    public String summary() {
        return "WorkerShift:" + String.valueOf(workerNo);
    }

    /** 结束分钟不大于开始分钟视为跨夜。 */
    public boolean overnight() {
        return endMin <= startMin;
    }

}
