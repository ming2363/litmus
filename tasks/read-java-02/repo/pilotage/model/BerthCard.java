package pilotage.model;

import java.util.ArrayList;
import java.util.List;

/** 泊位卡片 */
public final class BerthCard {
    public final String code;
    public final String name;
    public final int lengthM;
    public final int draughtM;
    public final String state;
    public final boolean nightOk;

    public BerthCard(String code, String name, int lengthM, int draughtM, String state, boolean nightOk) {
        this.code = code;
        this.name = name;
        this.lengthM = lengthM;
        this.draughtM = draughtM;
        this.state = state;
        this.nightOk = nightOk;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (code == null || code.length() < 2 || code.length() > 16) {
            errors.add("code");
        }
        if (name == null || name.trim().isEmpty() || name.trim().length() > 40) {
            errors.add("name");
        }
        if (lengthM < 30 || lengthM > 420) {
            errors.add("lengthM");
        }
        if (draughtM < 2 || draughtM > 20) {
            errors.add("draughtM");
        }
        if (!("active".equals(state) || "idle".equals(state) || "closed".equals(state) || "repair".equals(state))) {
            errors.add("state");
        }

        return errors;
    }

    public String summary() {
        return "BerthCard:" + String.valueOf(code);
    }

    /** 吃水不超过限制且未关闭。 */
    public boolean canTake(int draught) {
        if ("closed".equals(state)) {
            return false;
        }
        return draught <= draughtM;
    }

}
