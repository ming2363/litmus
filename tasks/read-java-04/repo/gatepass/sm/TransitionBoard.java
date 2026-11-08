package gatepass.sm;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** 可变的边表。remove 按起点和终点删除，不看守卫。 */
public final class TransitionBoard {
    /** 一条边。 */
    public static final class Edge {
        public final PassState to;
        public final Guard guard;

        public Edge(PassState to, Guard guard) {
            this.to = to;
            this.guard = guard;
        }
    }

    private final Map<PassState, List<Edge>> edges = new EnumMap<PassState, List<Edge>>(PassState.class);

    public void add(PassState from, PassState to, Guard guard) {
        List<Edge> list = edges.get(from);
        if (list == null) {
            list = new ArrayList<Edge>();
            edges.put(from, list);
        }
        list.add(new Edge(to, guard));
    }

    public void remove(PassState from, PassState to) {
        List<Edge> list = edges.get(from);
        if (list == null) {
            return;
        }
        List<Edge> kept = new ArrayList<Edge>();
        for (int i = 0; i < list.size(); i++) {
            if (list.get(i).to != to) {
                kept.add(list.get(i));
            }
        }
        edges.put(from, kept);
    }

    public List<Edge> from(PassState state) {
        List<Edge> list = edges.get(state);
        if (list == null) {
            return new ArrayList<Edge>();
        }
        return new ArrayList<Edge>(list);
    }
}
