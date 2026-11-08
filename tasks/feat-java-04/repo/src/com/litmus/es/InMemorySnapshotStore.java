package com.litmus.es;

import java.util.Optional;

/**
 * 内存快照存储（起始实现尚未完成）。
 */
public class InMemorySnapshotStore implements SnapshotStore {
    @Override
    public void save(Snapshot snapshot) {
        throw new UnsupportedOperationException("InMemorySnapshotStore.save 尚未实现");
    }

    @Override
    public Optional<Snapshot> loadLatest(String aggregateId) {
        throw new UnsupportedOperationException("InMemorySnapshotStore.loadLatest 尚未实现");
    }

    @Override
    public Optional<Snapshot> loadLatestAtOrBefore(String aggregateId, long maxVersion) {
        throw new UnsupportedOperationException("InMemorySnapshotStore.loadLatestAtOrBefore 尚未实现");
    }
}
