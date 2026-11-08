package com.litmus.log;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * 可见基础回归测试（不锁死旧输出格式）。
 */
public class AuditLoggerPublicTest {
    private static void assertTrue(boolean cond, String msg) {
        if (!cond) {
            throw new AssertionError(msg);
        }
    }

    public void testWriteAppendsSingleEntry() {
        AuditLogger logger = AuditLogger.defaultLogger();
        LogRecord record = new LogRecord(
                Instant.parse("2026-03-10T08:15:30Z"),
                LogLevel.INFO,
                "gateway",
                "user login ok");
        List<String> sink = new ArrayList<>();
        logger.write(record, sink);
        assertTrue(sink.size() == 1, "应写入一条日志");
        assertTrue(sink.get(0) != null && sink.get(0).contains("gateway"), "输出应包含组件名");
        assertTrue(sink.get(0).contains("user login ok"), "输出应包含消息正文");
    }

    public void testNullGuards() {
        AuditLogger logger = AuditLogger.defaultLogger();
        boolean threwRecord = false;
        try {
            logger.format(null);
        } catch (IllegalArgumentException ex) {
            threwRecord = true;
        }
        assertTrue(threwRecord, "record 为 null 时应抛出 IllegalArgumentException");

        boolean threwSink = false;
        try {
            logger.write(
                    new LogRecord(Instant.parse("2026-03-10T00:00:00Z"), LogLevel.INFO, "core", "ok"),
                    null);
        } catch (IllegalArgumentException ex) {
            threwSink = true;
        }
        assertTrue(threwSink, "sink 为 null 时应抛出 IllegalArgumentException");
    }
}
