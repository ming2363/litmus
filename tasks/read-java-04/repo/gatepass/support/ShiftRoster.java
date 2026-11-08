package gatepass.support;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 班次覆盖。同一人同一天只排一班。 */
public final class ShiftRoster {
    private ShiftRoster() {
    }

    public static Map<String, List<String>> assign(String[] people, String[] slots, int[] demand) {
        if (people.length == 0 || slots.length != demand.length) {
            throw new IllegalArgumentException("roster");
        }
        String[] names = Arrays.copyOf(people, people.length);
        Arrays.sort(names);
        Map<String, List<String>> table = new LinkedHashMap<String, List<String>>();
        List<String> used = new ArrayList<String>();
        int cursor = 0;
        for (int s = 0; s < slots.length; s++) {
            List<String> chosen = new ArrayList<String>();
            int guard = 0;
            while (chosen.size() < demand[s] && guard < names.length * 2) {
                String name = names[cursor % names.length];
                cursor += 1;
                guard += 1;
                String mark = name + "@" + dayOf(slots[s]);
                if (used.contains(mark)) {
                    continue;
                }
                used.add(mark);
                chosen.add(name);
            }
            table.put(slots[s], chosen);
        }
        return table;
    }

    private static String dayOf(String slot) {
        int cut = slot.indexOf('#');
        if (cut < 0) {
            return slot;
        }
        return slot.substring(0, cut);
    }
}
