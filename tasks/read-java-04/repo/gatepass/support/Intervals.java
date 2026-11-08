package gatepass.support;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/** 半开整数区间。 */
public final class Intervals {
    private Intervals() {
    }

    public static final class Span {
        public final int start;
        public final int end;

        public Span(int start, int end) {
            if (end < start) {
                throw new IllegalArgumentException("order");
            }
            this.start = start;
            this.end = end;
        }
    }

    public static List<Span> merge(List<Span> input) {
        List<Span> ordered = new ArrayList<Span>();
        for (int i = 0; i < input.size(); i++) {
            Span span = input.get(i);
            if (span.end > span.start) {
                ordered.add(span);
            }
        }
        Collections.sort(ordered, new Comparator<Span>() {
            @Override
            public int compare(Span left, Span right) {
                if (left.start != right.start) {
                    return left.start - right.start;
                }
                return left.end - right.end;
            }
        });
        List<Span> merged = new ArrayList<Span>();
        for (int i = 0; i < ordered.size(); i++) {
            Span span = ordered.get(i);
            if (merged.isEmpty()) {
                merged.add(span);
                continue;
            }
            Span last = merged.get(merged.size() - 1);
            if (span.start <= last.end) {
                merged.set(merged.size() - 1, new Span(last.start, Math.max(last.end, span.end)));
            } else {
                merged.add(span);
            }
        }
        return merged;
    }

    public static int totalLength(List<Span> input) {
        int total = 0;
        List<Span> merged = merge(input);
        for (int i = 0; i < merged.size(); i++) {
            Span span = merged.get(i);
            total += span.end - span.start;
        }
        return total;
    }
}
