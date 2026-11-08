package com.litmus.log;

import java.time.Instant;
import java.util.Objects;

/**
 * 不可变审计日志记录对象。
 */
public final class LogRecord {
    private final Instant timestamp;
    private final LogLevel level;
    private final String component;
    private final String message;

    public LogRecord(Instant timestamp, LogLevel level, String component, String message) {
        this.timestamp = Objects.requireNonNull(timestamp, "timestamp 不能为空");
        this.level = Objects.requireNonNull(level, "level 不能为空");
        this.component = component;
        this.message = message;
    }

    public Instant timestamp() {
        return timestamp;
    }

    public LogLevel level() {
        return level;
    }

    public String component() {
        return component;
    }

    public String message() {
        return message;
    }
}
