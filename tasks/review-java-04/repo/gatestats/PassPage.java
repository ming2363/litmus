package gatestats;

import java.util.List;

/** 过车记录分页。 */
public final class PassPage {
    private PassPage() {
    }

    /**
     * page 从 1 开始。
     * 最后一页不足 size 时返回剩余元素，不抛出 IndexOutOfBoundsException。
     */
    public static List<PassRow> page(List<PassRow> all, int page, int size) {
        if (page < 1 || size < 1) {
            throw new IllegalArgumentException("page");
        }
        int from = (page - 1) * size;
        int to = from + size;
        return all.subList(from, to);
    }
}
