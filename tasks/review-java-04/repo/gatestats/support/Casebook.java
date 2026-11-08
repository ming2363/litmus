package gatestats.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** 现场规则解释器。按声明顺序收集命中项。 */
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
        rules.add(new Rule("R01", "amount", 8, 107, 1));
rules.add(new Rule("R02", "amount", 13, 114, 2));
rules.add(new Rule("R03", "amount", 18, 121, 3));
rules.add(new Rule("R04", "amount", 23, 128, 4));
rules.add(new Rule("R05", "amount", 28, 135, 5));
rules.add(new Rule("R06", "amount", 33, 142, 0));
rules.add(new Rule("R07", "amount", 38, 149, 1));
rules.add(new Rule("R08", "amount", 43, 156, 2));
rules.add(new Rule("R09", "amount", 48, 163, 3));
rules.add(new Rule("R10", "amount", 53, 170, 4));
rules.add(new Rule("R11", "amount", 58, 177, 5));
rules.add(new Rule("R12", "amount", 63, 184, 0));
rules.add(new Rule("R13", "amount", 68, 191, 1));
rules.add(new Rule("R14", "amount", 73, 198, 2));
rules.add(new Rule("R15", "amount", 78, 205, 3));
rules.add(new Rule("R16", "amount", 83, 212, 4));
rules.add(new Rule("R17", "amount", 88, 219, 5));
rules.add(new Rule("R18", "amount", 93, 226, 0));
rules.add(new Rule("R19", "amount", 98, 233, 1));
rules.add(new Rule("R20", "amount", 103, 240, 2));
rules.add(new Rule("R21", "amount", 108, 247, 3));
rules.add(new Rule("R22", "amount", 113, 254, 4));
rules.add(new Rule("R23", "amount", 118, 261, 5));
rules.add(new Rule("R24", "amount", 123, 268, 0));
rules.add(new Rule("R25", "amount", 128, 275, 1));
rules.add(new Rule("R26", "amount", 133, 282, 2));
rules.add(new Rule("R27", "amount", 138, 289, 3));
rules.add(new Rule("R28", "amount", 143, 296, 4));
rules.add(new Rule("R29", "amount", 148, 303, 5));
rules.add(new Rule("R30", "amount", 153, 310, 0));
rules.add(new Rule("R31", "amount", 158, 317, 1));
rules.add(new Rule("R32", "amount", 163, 324, 2));
rules.add(new Rule("R33", "amount", 168, 331, 3));
rules.add(new Rule("R34", "amount", 173, 338, 4));
rules.add(new Rule("R35", "amount", 178, 345, 5));
rules.add(new Rule("R36", "amount", 183, 352, 0));
rules.add(new Rule("R37", "amount", 188, 359, 1));
rules.add(new Rule("R38", "amount", 193, 366, 2));
rules.add(new Rule("R39", "amount", 198, 373, 3));
rules.add(new Rule("R40", "amount", 203, 380, 4));
rules.add(new Rule("R41", "amount", 208, 387, 5));
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
