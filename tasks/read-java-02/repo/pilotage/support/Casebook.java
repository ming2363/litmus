package pilotage.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** 引航规则解释器。按声明顺序收集命中项。 */
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
        rules.add(new Rule("R01", "draught_cm", 840, 107, 1));
rules.add(new Rule("R02", "draught_cm", 880, 114, 2));
rules.add(new Rule("R03", "draught_cm", 920, 121, 3));
rules.add(new Rule("R04", "draught_cm", 960, 128, 4));
rules.add(new Rule("R05", "draught_cm", 1000, 135, 5));
rules.add(new Rule("R06", "draught_cm", 1040, 142, 0));
rules.add(new Rule("R07", "draught_cm", 1080, 149, 1));
rules.add(new Rule("R08", "draught_cm", 1120, 156, 2));
rules.add(new Rule("R09", "draught_cm", 1160, 163, 3));
rules.add(new Rule("R10", "draught_cm", 1200, 170, 4));
rules.add(new Rule("R11", "draught_cm", 1240, 177, 5));
rules.add(new Rule("R12", "draught_cm", 1280, 184, 0));
rules.add(new Rule("R13", "draught_cm", 1320, 191, 1));
rules.add(new Rule("R14", "draught_cm", 1360, 198, 2));
rules.add(new Rule("R15", "draught_cm", 1400, 205, 3));
rules.add(new Rule("R16", "draught_cm", 1440, 212, 4));
rules.add(new Rule("R17", "draught_cm", 1480, 219, 5));
rules.add(new Rule("R18", "draught_cm", 1520, 226, 0));
rules.add(new Rule("R19", "draught_cm", 1560, 233, 1));
rules.add(new Rule("R20", "draught_cm", 1600, 240, 2));
rules.add(new Rule("R21", "draught_cm", 1640, 247, 3));
rules.add(new Rule("R22", "draught_cm", 1680, 254, 4));
rules.add(new Rule("R23", "draught_cm", 1720, 261, 5));
rules.add(new Rule("R24", "draught_cm", 1760, 268, 0));
rules.add(new Rule("R25", "draught_cm", 1800, 275, 1));
rules.add(new Rule("R26", "draught_cm", 1840, 282, 2));
rules.add(new Rule("R27", "draught_cm", 1880, 289, 3));
rules.add(new Rule("R28", "draught_cm", 1920, 296, 4));
rules.add(new Rule("R29", "draught_cm", 1960, 303, 5));
rules.add(new Rule("R30", "draught_cm", 2000, 310, 0));
rules.add(new Rule("R31", "draught_cm", 2040, 317, 1));
rules.add(new Rule("R32", "draught_cm", 2080, 324, 2));
rules.add(new Rule("R33", "draught_cm", 2120, 331, 3));
rules.add(new Rule("R34", "draught_cm", 2160, 338, 4));
rules.add(new Rule("R35", "draught_cm", 2200, 345, 5));
rules.add(new Rule("R36", "draught_cm", 2240, 352, 0));
rules.add(new Rule("R37", "draught_cm", 2280, 359, 1));
rules.add(new Rule("R38", "draught_cm", 2320, 366, 2));
rules.add(new Rule("R39", "draught_cm", 2360, 373, 3));
rules.add(new Rule("R40", "draught_cm", 2400, 380, 4));
rules.add(new Rule("R41", "draught_cm", 2440, 387, 5));
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
