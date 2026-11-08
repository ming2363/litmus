package com.litmus.es;

public class InventoryPublicTest {

    private static void assertEq(long expected, long actual, String msg) {
        if (expected != actual) {
            throw new AssertionError(msg + " (expected=" + expected + ", actual=" + actual + ")");
        }
    }

    public void testBasicReceiveAndReserveReplay() {
        EventStore eventStore = new InMemoryEventStore();
        SnapshotStore noOpSnapshots = new SnapshotStore() {
            @Override
            public void save(Snapshot snapshot) {
            }

            @Override
            public java.util.Optional<Snapshot> loadLatest(String aggregateId) {
                return java.util.Optional.empty();
            }

            @Override
            public java.util.Optional<Snapshot> loadLatestAtOrBefore(String aggregateId, long maxVersion) {
                return java.util.Optional.empty();
            }
        };
        InventoryRepository repo = new InventoryRepository(eventStore, noOpSnapshots, 0);
        InventoryState s1 = repo.receiveStock("SKU-100", "BATCH-1", 50, 0L);
        assertEq(1L, s1.getVersion(), "v1");
        assertEq(50, s1.getOnHand(), "onHand");

        InventoryState s2 = repo.reserveStock("SKU-100", "ORD-1", 15, 1L);
        assertEq(2L, s2.getVersion(), "v2");
        assertEq(15, s2.getReserved(), "reserved");
        assertEq(35, s2.available(), "available");

        InventoryState reloaded = repo.load("SKU-100");
        assertEq(2L, reloaded.getVersion(), "reloaded version");
        assertEq(35, reloaded.available(), "reloaded available");
    }
}
