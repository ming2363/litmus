package sliparchive.support;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/** 滑动窗口最值。 */
public final class Sliding {
    private Sliding() {
    }

    public static List<Integer> windowMax(List<Integer> values, int width) {
        if (width <= 0) {
            throw new IllegalArgumentException("width");
        }
        Deque<Integer> dq = new ArrayDeque<Integer>();
        List<Integer> out = new ArrayList<Integer>();
        for (int idx = 0; idx < values.size(); idx++) {
            while (!dq.isEmpty() && dq.peekFirst().intValue() <= idx - width) {
                dq.removeFirst();
            }
            int value = values.get(idx).intValue();
            while (!dq.isEmpty() && values.get(dq.peekLast().intValue()).intValue() <= value) {
                dq.removeLast();
            }
            dq.addLast(Integer.valueOf(idx));
            out.add(values.get(dq.peekFirst().intValue()));
        }
        return out;
    }
}
