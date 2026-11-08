package com.litmus.ticket;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

/**
 * 可见工单查询与更新基础测试。
 */
public class TicketDaoPublicTest {
    private static void assertEquals(Object expected, Object actual, String msg) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new AssertionError(msg + "，期望=" + expected + "，实际=" + actual);
        }
    }

    private InMemoryTicketDb createSampleDb() {
        InMemoryTicketDb db = new InMemoryTicketDb();
        db.insert(new Ticket(1, "Gateway timeout under load", "alice", "OPEN", 2, "investigating"));
        db.insert(new Ticket(2, "Export CSV header mismatch", "bob", "OPEN", 3, "new"));
        db.insert(new Ticket(3, "Auth token refresh race", "alice", "CLOSED", 1, "resolved"));
        return db;
    }

    public void testBasicQuerySearchAndUpdate() throws SQLException {
        InMemoryTicketDb db = createSampleDb();
        TicketDao dao = new TicketDao();
        try (Connection conn = db.openConnection()) {
            List<Ticket> aliceOpen = dao.findByAssigneeAndStatus(conn, "alice", "OPEN");
            assertEquals(1, aliceOpen.size(), "查询 alice 的 OPEN 工单失败");
            assertEquals(1, aliceOpen.get(0).id(), "工单 ID 不匹配");

            List<Ticket> found = dao.searchByTitleKeyword(conn, "timeout");
            assertEquals(1, found.size(), "关键字搜索失败");
            assertEquals(1, found.get(0).id(), "关键字搜索结果 ID 不匹配");

            int updated = dao.updatePriorityAndNote(conn, 2, 1, "escalated to p1");
            assertEquals(1, updated, "更新影响行数应为 1");
            assertEquals(1, db.getById(2).priority(), "优先级未更新");
            assertEquals("escalated to p1", db.getById(2).note(), "备注未更新");
        }
    }
}
