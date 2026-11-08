package yardorder.support;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** 页码从 1 开始，不足一页时截断。 */
public final class Pager {
    private Pager() {
    }

    public static <T> List<T> page(List<T> rows, int page, int size) {
        if (page < 1 || size < 1) {
            throw new IllegalArgumentException("page");
        }
        int start = (page - 1) * size;
        if (start >= rows.size()) {
            return Collections.emptyList();
        }
        int end = Math.min(start + size, rows.size());
        return new ArrayList<T>(rows.subList(start, end));
    }

    public static int pageCount(int total, int size) {
        if (size < 1 || total < 0) {
            throw new IllegalArgumentException("size");
        }
        if (total == 0) {
            return 0;
        }
        return (total + size - 1) / size;
    }
}
