package coldvault.support;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** 部门树汇总。 */
public final class DeptRollup {
    private DeptRollup() {
    }

    public static Map<String, Integer> rollup(List<String> nodes, Map<String, String> parentOf,
            Map<String, Integer> valueOf) {
        Map<String, List<String>> children = new HashMap<String, List<String>>();
        for (int i = 0; i < nodes.size(); i++) {
            children.put(nodes.get(i), new ArrayList<String>());
        }
        List<String> roots = new ArrayList<String>();
        for (int i = 0; i < nodes.size(); i++) {
            String node = nodes.get(i);
            String parent = parentOf.get(node);
            if (parent == null) {
                roots.add(node);
            } else {
                if (!children.containsKey(parent)) {
                    throw new IllegalArgumentException(parent);
                }
                children.get(parent).add(node);
            }
        }
        Map<String, Integer> totals = new HashMap<String, Integer>();
        for (int i = 0; i < roots.size(); i++) {
            walk(roots.get(i), children, valueOf, totals, new HashSet<String>());
        }
        return totals;
    }

    private static int walk(String node, Map<String, List<String>> children, Map<String, Integer> valueOf,
            Map<String, Integer> totals, Set<String> stack) {
        if (!stack.add(node)) {
            throw new IllegalArgumentException("cycle");
        }
        int total = valueOf.containsKey(node) ? valueOf.get(node).intValue() : 0;
        List<String> kids = children.get(node);
        for (int i = 0; i < kids.size(); i++) {
            total += walk(kids.get(i), children, valueOf, totals, stack);
        }
        stack.remove(node);
        totals.put(node, Integer.valueOf(total));
        return total;
    }
}
