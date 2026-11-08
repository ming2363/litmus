package holdledger.model;

import java.util.ArrayList;
import java.util.List;

/** 访客通行证 */
public final class BadgePass {
    public final String badgeNo;
    public final String holder;
    public final boolean validDay;
    public final boolean lost;

    public BadgePass(String badgeNo, String holder, boolean validDay, boolean lost) {
        this.badgeNo = badgeNo;
        this.holder = holder;
        this.validDay = validDay;
        this.lost = lost;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (badgeNo == null || badgeNo.length() < 2 || badgeNo.length() > 16) {
            errors.add("badgeNo");
        }
        if (holder == null || holder.trim().isEmpty() || holder.trim().length() > 40) {
            errors.add("holder");
        }


        return errors;
    }

    public String summary() {
        return "BadgePass:" + String.valueOf(badgeNo);
    }

    /** 当日有效且未挂失。 */
    public boolean dayPass() {
        return validDay && !lost;
    }

}
