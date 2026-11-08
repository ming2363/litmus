package com.litmus.ticket;

import java.util.Objects;

/**
 * 不可变工单实体模型。
 */
public final class Ticket {
    private final int id;
    private final String title;
    private final String assignee;
    private final String status;
    private final int priority;
    private final String note;

    public Ticket(int id, String title, String assignee, String status, int priority, String note) {
        this.id = id;
        this.title = Objects.requireNonNull(title, "title 不能为空");
        this.assignee = Objects.requireNonNull(assignee, "assignee 不能为空");
        this.status = Objects.requireNonNull(status, "status 不能为空");
        this.priority = priority;
        this.note = note == null ? "" : note;
    }

    public int id() {
        return id;
    }

    public String title() {
        return title;
    }

    public String assignee() {
        return assignee;
    }

    public String status() {
        return status;
    }

    public int priority() {
        return priority;
    }

    public String note() {
        return note;
    }
}
