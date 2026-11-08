package coldvault.model;

import java.util.ArrayList;
import java.util.List;

/** 船舶挂靠 */
public final class VoyageCall {
    public final String voyageNo;
    public final String terminal;
    public final int loaM;
    public final String agent;
    public final String status;

    public VoyageCall(String voyageNo, String terminal, int loaM, String agent, String status) {
        this.voyageNo = voyageNo;
        this.terminal = terminal;
        this.loaM = loaM;
        this.agent = agent;
        this.status = status;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (voyageNo == null || voyageNo.length() < 2 || voyageNo.length() > 16) {
            errors.add("voyageNo");
        }
        if (terminal == null || terminal.trim().isEmpty() || terminal.trim().length() > 40) {
            errors.add("terminal");
        }
        if (loaM < 40 || loaM > 400) {
            errors.add("loaM");
        }
        if (agent == null || agent.trim().isEmpty() || agent.trim().length() > 40) {
            errors.add("agent");
        }
        if (!("planned".equals(status) || "alongside".equals(status) || "sailed".equals(status))) {
            errors.add("status");
        }
        return errors;
    }

    public String summary() {
        return "VoyageCall:" + String.valueOf(voyageNo);
    }

    /** 航次号与码头都相同。 */
    public boolean sameCall(VoyageCall other) {
        return voyageNo.equals(other.voyageNo) && terminal.equals(other.terminal);
    }

}
