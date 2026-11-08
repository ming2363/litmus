package admission;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 有容量上限的访客缓存。满员时按访问先后淘汰，次数只在时间相同才参与比较。
 */
public final class VisitCache {

    private static final class Node {
        private final String key;
        private String value;
        private int count;
        private long lastAccess;

        private Node(String key, String value, int count, long lastAccess) {
            this.key = key;
            this.value = value;
            this.count = count;
            this.lastAccess = lastAccess;
        }
    }

    private final int capacity;
    private final Map<String, Node> nodes = new LinkedHashMap<String, Node>();
    private long clock;

    public VisitCache(int capacity) {
        if (capacity < 1) {
            throw new IllegalArgumentException("容量必须为正");
        }
        this.capacity = capacity;
    }

    public String get(String key) {
        if (key == null) {
            throw new NullPointerException("key");
        }
        Node node = nodes.get(key);
        if (node == null) {
            return null;
        }
        touch(node);
        return node.value;
    }

    public void put(String key, String value) {
        if (key == null || value == null) {
            throw new NullPointerException("key/value");
        }
        Node existing = nodes.get(key);
        if (existing != null) {
            existing.value = value;
            touch(existing);
            return;
        }
        if (nodes.size() >= capacity) {
            evictOne();
        }
        clock++;
        nodes.put(key, new Node(key, value, 1, clock));
    }

    public int size() {
        return nodes.size();
    }

    public int accessCount(String key) {
        if (key == null) {
            throw new NullPointerException("key");
        }
        Node node = nodes.get(key);
        return node == null ? 0 : node.count;
    }

    private void touch(Node node) {
        node.count++;
        clock++;
        node.lastAccess = clock;
    }

    private void evictOne() {
        Node victim = null;
        for (Node node : nodes.values()) {
            if (victim == null || earlier(node, victim)) {
                victim = node;
            }
        }
        nodes.remove(victim.key);
    }

    /** 时间更早的优先；时间相同再看次数。 */
    private boolean earlier(Node left, Node right) {
        if (left.lastAccess != right.lastAccess) {
            return left.lastAccess < right.lastAccess;
        }
        return left.count < right.count;
    }
}
