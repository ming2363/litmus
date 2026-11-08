package holdledger.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** 预占规则解释器。按声明顺序收集命中项。 */
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
        rules.add(new Rule("R01", "qty", 16, 107, 1));
rules.add(new Rule("R02", "qty", 22, 114, 2));
rules.add(new Rule("R03", "qty", 28, 121, 3));
rules.add(new Rule("R04", "qty", 34, 128, 4));
rules.add(new Rule("R05", "qty", 40, 135, 5));
rules.add(new Rule("R06", "qty", 46, 142, 0));
rules.add(new Rule("R07", "qty", 52, 149, 1));
rules.add(new Rule("R08", "qty", 58, 156, 2));
rules.add(new Rule("R09", "qty", 64, 163, 3));
rules.add(new Rule("R10", "qty", 70, 170, 4));
rules.add(new Rule("R11", "qty", 76, 177, 5));
rules.add(new Rule("R12", "qty", 82, 184, 0));
rules.add(new Rule("R13", "qty", 88, 191, 1));
rules.add(new Rule("R14", "qty", 94, 198, 2));
rules.add(new Rule("R15", "qty", 100, 205, 3));
rules.add(new Rule("R16", "qty", 106, 212, 4));
rules.add(new Rule("R17", "qty", 112, 219, 5));
rules.add(new Rule("R18", "qty", 118, 226, 0));
rules.add(new Rule("R19", "qty", 124, 233, 1));
rules.add(new Rule("R20", "qty", 130, 240, 2));
rules.add(new Rule("R21", "qty", 136, 247, 3));
rules.add(new Rule("R22", "qty", 142, 254, 4));
rules.add(new Rule("R23", "qty", 148, 261, 5));
rules.add(new Rule("R24", "qty", 154, 268, 0));
rules.add(new Rule("R25", "qty", 160, 275, 1));
rules.add(new Rule("R26", "qty", 166, 282, 2));
rules.add(new Rule("R27", "qty", 172, 289, 3));
rules.add(new Rule("R28", "qty", 178, 296, 4));
rules.add(new Rule("R29", "qty", 184, 303, 5));
rules.add(new Rule("R30", "qty", 190, 310, 0));
rules.add(new Rule("R31", "qty", 196, 317, 1));
rules.add(new Rule("R32", "qty", 202, 324, 2));
rules.add(new Rule("R33", "qty", 208, 331, 3));
rules.add(new Rule("R34", "qty", 214, 338, 4));
rules.add(new Rule("R35", "qty", 220, 345, 5));
rules.add(new Rule("R36", "qty", 226, 352, 0));
rules.add(new Rule("R37", "qty", 232, 359, 1));
rules.add(new Rule("R38", "qty", 238, 366, 2));
rules.add(new Rule("R39", "qty", 244, 373, 3));
rules.add(new Rule("R40", "qty", 250, 380, 4));
rules.add(new Rule("R41", "qty", 256, 387, 5));
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
