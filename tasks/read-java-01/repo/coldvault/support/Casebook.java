package coldvault.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** 温区规则解释器。按声明顺序收集命中项。 */
public final class Casebook {
    public static final class Rule {
        public final String id;
        public final String field;
        public final int threshold;
        public final int score;
        public final int extraMod;

        public Rule(String id, String field, int threshold, int score, int extraMod) {
            this.id = id;
            this.field = field;
            this.threshold = threshold;
            this.score = score;
            this.extraMod = extraMod;
        }
    }

    private final List<Rule> rules = new ArrayList<Rule>();

    public Casebook() {
        rules.add(new Rule("R01", "probe_c", 22, 107, 1));
rules.add(new Rule("R02", "probe_c", 40, 114, 2));
rules.add(new Rule("R03", "probe_c", 58, 121, 3));
rules.add(new Rule("R04", "probe_c", 76, 128, 4));
rules.add(new Rule("R05", "probe_c", 94, 135, 5));
rules.add(new Rule("R06", "probe_c", 112, 142, 0));
rules.add(new Rule("R07", "probe_c", 130, 149, 1));
rules.add(new Rule("R08", "probe_c", 148, 156, 2));
rules.add(new Rule("R09", "probe_c", 166, 163, 3));
rules.add(new Rule("R10", "probe_c", 184, 170, 4));
rules.add(new Rule("R11", "probe_c", 202, 177, 5));
rules.add(new Rule("R12", "probe_c", 220, 184, 0));
rules.add(new Rule("R13", "probe_c", 238, 191, 1));
rules.add(new Rule("R14", "probe_c", 256, 198, 2));
rules.add(new Rule("R15", "probe_c", 274, 205, 3));
rules.add(new Rule("R16", "probe_c", 292, 212, 4));
rules.add(new Rule("R17", "probe_c", 310, 219, 5));
rules.add(new Rule("R18", "probe_c", 328, 226, 0));
rules.add(new Rule("R19", "probe_c", 346, 233, 1));
rules.add(new Rule("R20", "probe_c", 364, 240, 2));
rules.add(new Rule("R21", "probe_c", 382, 247, 3));
rules.add(new Rule("R22", "probe_c", 400, 254, 4));
rules.add(new Rule("R23", "probe_c", 418, 261, 5));
rules.add(new Rule("R24", "probe_c", 436, 268, 0));
rules.add(new Rule("R25", "probe_c", 454, 275, 1));
rules.add(new Rule("R26", "probe_c", 472, 282, 2));
rules.add(new Rule("R27", "probe_c", 490, 289, 3));
rules.add(new Rule("R28", "probe_c", 508, 296, 4));
rules.add(new Rule("R29", "probe_c", 526, 303, 5));
rules.add(new Rule("R30", "probe_c", 544, 310, 0));
rules.add(new Rule("R31", "probe_c", 562, 317, 1));
rules.add(new Rule("R32", "probe_c", 580, 324, 2));
rules.add(new Rule("R33", "probe_c", 598, 331, 3));
rules.add(new Rule("R34", "probe_c", 616, 338, 4));
rules.add(new Rule("R35", "probe_c", 634, 345, 5));
rules.add(new Rule("R36", "probe_c", 652, 352, 0));
rules.add(new Rule("R37", "probe_c", 670, 359, 1));
rules.add(new Rule("R38", "probe_c", 688, 366, 2));
rules.add(new Rule("R39", "probe_c", 706, 373, 3));
rules.add(new Rule("R40", "probe_c", 724, 380, 4));
rules.add(new Rule("R41", "probe_c", 742, 387, 5));
    }

    /** 命中的规则 id。缺字段按 0。 */
    public List<String> hits(Map<String, Integer> record) {
        List<String> found = new ArrayList<String>();
        for (int i = 0; i < rules.size(); i++) {
            Rule rule = rules.get(i);
            int left = 0;
            if (record.containsKey(rule.field)) {
                left = record.get(rule.field).intValue();
            }
            boolean ok = rule.extraMod == 2 ? left < rule.threshold : left >= rule.threshold;
            if (!ok) {
                continue;
            }
            found.add(rule.id);
        }
        return found;
    }

    /** 命中分合计。extraMod 非 0 且数量能整除时加五分之一。 */
    public int score(Map<String, Integer> record, int extra) {
        int total = 0;
        List<String> found = hits(record);
        for (int i = 0; i < rules.size(); i++) {
            Rule rule = rules.get(i);
            if (!found.contains(rule.id)) {
                continue;
            }
            int bonus = 0;
            if (rule.extraMod != 0 && extra % (rule.extraMod + 1) == 0) {
                bonus = rule.score / 5;
            }
            total += rule.score + bonus;
        }
        return total;
    }
}
