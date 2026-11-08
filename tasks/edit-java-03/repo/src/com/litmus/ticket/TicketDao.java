package com.litmus.ticket;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * 工单数据访问对象（当前存在 SQL 字符串拼接问题）。
 */
public final class TicketDao {
    public List<Ticket> findByAssigneeAndStatus(Connection conn, String assignee, String status) throws SQLException {
        if (conn == null || assignee == null || status == null) {
            throw new IllegalArgumentException("参数不能为空");
        }
        String sql = "SELECT id, title, assignee, status, priority, note FROM tickets "
                + "WHERE assignee = '" + assignee + "' AND status = '" + status + "' ORDER BY id ASC";
        List<Ticket> result = new ArrayList<>();
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                result.add(mapRow(rs));
            }
        }
        return result;
    }

    public List<Ticket> searchByTitleKeyword(Connection conn, String keyword) throws SQLException {
        if (conn == null || keyword == null) {
            throw new IllegalArgumentException("参数不能为空");
        }
        String sql = "SELECT id, title, assignee, status, priority, note FROM tickets "
                + "WHERE title LIKE '%" + keyword + "%' ORDER BY id ASC";
        List<Ticket> result = new ArrayList<>();
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                result.add(mapRow(rs));
            }
        }
        return result;
    }

    public int updatePriorityAndNote(Connection conn, int id, int newPriority, String note) throws SQLException {
        if (conn == null || note == null) {
            throw new IllegalArgumentException("参数不能为空");
        }
        String sql = "UPDATE tickets SET priority = " + newPriority
                + ", note = '" + note + "' WHERE id = " + id;
        try (Statement stmt = conn.createStatement()) {
            return stmt.executeUpdate(sql);
        }
    }

    private static Ticket mapRow(ResultSet rs) throws SQLException {
        return new Ticket(
                rs.getInt("id"),
                rs.getString("title"),
                rs.getString("assignee"),
                rs.getString("status"),
                rs.getInt("priority"),
                rs.getString("note"));
    }
}
