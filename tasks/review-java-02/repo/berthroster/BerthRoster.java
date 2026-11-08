package berthroster;

import java.util.HashMap;
import java.util.Map;

/**
 * 泊位当值表。
 * 调度池会从多个线程调用本类的公开方法。
 */
public final class BerthRoster {
    private final Map<String, Worker> roster = new HashMap<String, Worker>();

    /** 已持锁的认领，检查和写入在同一把锁里。 */
    public synchronized Worker claimLocked(String berthId) {
        Worker current = roster.get(berthId);
        if (current == null || current.isReleased()) {
            Worker created = Worker.hire(berthId);
            roster.put(berthId, created);
            return created;
        }
        return current;
    }

    /** 新的快速认领。 */
    public Worker claim(String berthId) {
        Worker current = roster.get(berthId);
        if (current == null || current.isReleased()) {
            Worker created = Worker.hire(berthId);
            roster.put(berthId, created);
            return created;
        }
        return current;
    }

    public synchronized void release(String berthId) {
        Worker current = roster.get(berthId);
        if (current != null) {
            current.release();
        }
    }
}
