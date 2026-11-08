package gatepass.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** 闸口规则解释器。按声明顺序收集命中项。 */
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
        rules.add(new Rule("R01", "wait_min", 29, 107, 1));
rules.add(new Rule("R02", "wait_min", 38, 114, 2));
rules.add(new Rule("R03", "wait_min", 47, 121, 3));
rules.add(new Rule("R04", "wait_min", 56, 128, 4));
rules.add(new Rule("R05", "wait_min", 65, 135, 5));
rules.add(new Rule("R06", "wait_min", 74, 142, 0));
rules.add(new Rule("R07", "wait_min", 83, 149, 1));
rules.add(new Rule("R08", "wait_min", 92, 156, 2));
rules.add(new Rule("R09", "wait_min", 101, 163, 3));
rules.add(new Rule("R10", "wait_min", 110, 170, 4));
rules.add(new Rule("R11", "wait_min", 119, 177, 5));
rules.add(new Rule("R12", "wait_min", 128, 184, 0));
rules.add(new Rule("R13", "wait_min", 137, 191, 1));
rules.add(new Rule("R14", "wait_min", 146, 198, 2));
rules.add(new Rule("R15", "wait_min", 155, 205, 3));
rules.add(new Rule("R16", "wait_min", 164, 212, 4));
rules.add(new Rule("R17", "wait_min", 173, 219, 5));
rules.add(new Rule("R18", "wait_min", 182, 226, 0));
rules.add(new Rule("R19", "wait_min", 191, 233, 1));
rules.add(new Rule("R20", "wait_min", 200, 240, 2));
rules.add(new Rule("R21", "wait_min", 209, 247, 3));
rules.add(new Rule("R22", "wait_min", 218, 254, 4));
rules.add(new Rule("R23", "wait_min", 227, 261, 5));
rules.add(new Rule("R24", "wait_min", 236, 268, 0));
rules.add(new Rule("R25", "wait_min", 245, 275, 1));
rules.add(new Rule("R26", "wait_min", 254, 282, 2));
rules.add(new Rule("R27", "wait_min", 263, 289, 3));
rules.add(new Rule("R28", "wait_min", 272, 296, 4));
rules.add(new Rule("R29", "wait_min", 281, 303, 5));
rules.add(new Rule("R30", "wait_min", 290, 310, 0));
rules.add(new Rule("R31", "wait_min", 299, 317, 1));
rules.add(new Rule("R32", "wait_min", 308, 324, 2));
rules.add(new Rule("R33", "wait_min", 317, 331, 3));
rules.add(new Rule("R34", "wait_min", 326, 338, 4));
rules.add(new Rule("R35", "wait_min", 335, 345, 5));
rules.add(new Rule("R36", "wait_min", 344, 352, 0));
rules.add(new Rule("R37", "wait_min", 353, 359, 1));
rules.add(new Rule("R38", "wait_min", 362, 366, 2));
rules.add(new Rule("R39", "wait_min", 371, 373, 3));
rules.add(new Rule("R40", "wait_min", 380, 380, 4));
rules.add(new Rule("R41", "wait_min", 389, 387, 5));
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
