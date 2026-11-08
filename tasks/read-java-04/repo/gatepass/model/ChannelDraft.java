package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 航道水深 */
public final class ChannelDraft {
    public final String channel;
    public final int depthM;
    public final String surveyDay;

    public ChannelDraft(String channel, int depthM, String surveyDay) {
        this.channel = channel;
        this.depthM = depthM;
        this.surveyDay = surveyDay;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (channel == null || channel.length() < 2 || channel.length() > 16) {
            errors.add("channel");
        }
        if (depthM < 1 || depthM > 30) {
            errors.add("depthM");
        }
        if (surveyDay == null || surveyDay.trim().isEmpty() || surveyDay.trim().length() > 40) {
            errors.add("surveyDay");
        }
        return errors;
    }

    public String summary() {
        return "ChannelDraft:" + String.valueOf(channel);
    }

    /** 富裕水深。 */
    public int underKeel(int draught) {
        return depthM - draught;
    }

}
