package com.litmus.es;

import java.util.Optional;

/**
 * 聚合快照存储接口。
 */
public interface SnapshotStore {
    void save(Snapshot snapshot);

    Optional<Snapshot> loadLatest(String aggregateId);

    Optional<Snapshot> loadLatestAtOrBefore(String aggregateId, long maxVersion);
}
