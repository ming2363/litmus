package com.litmus.log;

import java.util.List;
import java.util.Locale;

/**
 * 审计日志格式化与输出器。
 */
public final class AuditLogger {
    private static final AuditLogger INSTANCE = new AuditLogger();

    private AuditLogger() {
    }

    public static AuditLogger defaultLogger() {
        return INSTANCE;
    }

    /**
     * 将单条日志记录格式化为字符串。
     */
    public String format(LogRecord record) {
        if (record == null) {
            throw new IllegalArgumentException("record 不能为空");
        }
        long millis = record.timestamp().toEpochMilli();
        String lvl = record.level().name().toLowerCase(Locale.ROOT);
        String comp = record.component() == null ? "unknown" : record.component().trim();
        String msg = record.message() == null ? "" : record.message();
        return "[" + millis + "] " + lvl + " (" + comp + "): " + msg;
    }

    /**
     * 格式化日志并追加到输出目标列表。
     */
    public void write(LogRecord record, List<String> sink) {
        if (sink == null) {
            throw new IllegalArgumentException("sink 不能为空");
        }
        sink.add(format(record));
    }
}
