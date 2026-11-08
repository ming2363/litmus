package pilotage.model;

import java.util.ArrayList;
import java.util.List;

/** 甚高频日志 */
public final class RadioLog {
    public final String logNo;
    public final int channel;
    public final String party;

    public RadioLog(String logNo, int channel, String party) {
        this.logNo = logNo;
        this.channel = channel;
        this.party = party;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (logNo == null || logNo.length() < 2 || logNo.length() > 16) {
            errors.add("logNo");
        }
        if (channel < 1 || channel > 88) {
            errors.add("channel");
        }
        if (party == null || party.trim().isEmpty() || party.trim().length() > 40) {
            errors.add("party");
        }
        return errors;
    }

    public String summary() {
        return "RadioLog:" + String.valueOf(logNo);
    }

    /** 16 频道视为遇险。 */
    public boolean distress() {
        return channel == 16;
    }

}
