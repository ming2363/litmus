package com.litmus.signing;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 北港单证令牌缓存。
 * 命中、淘汰和发布必须放在 lock 里；签名器的 sign 不能占着这把锁。
 */
public final class TokenBroker {

    /** 签名器。实现由调用方提供，可能阻塞。 */
    public interface Signer {
        byte[] sign(byte[] material);
    }

    /** 可替换时钟，单位是毫秒。 */
    public interface Clock {
        long now();
    }

    /** 不可变令牌。signature 是签名字节的副本。 */
    public static final class Token {
        public final String clientId;
        public final String subject;
        public final long expiresAt;
        public final byte[] signature;

        public Token(String clientId, String subject, long expiresAt, byte[] signature) {
            this.clientId = clientId;
            this.subject = subject;
            this.expiresAt = expiresAt;
            this.signature = signature.clone();
        }
    }

    /** 计数器快照。读取时复制，不暴露内部集合。 */
    public static final class Snapshot {
        public final long totalRequests;
        public final long cacheHits;
        public final long upstreamSignCalls;
        public final long evictionCount;
        public final int cacheSize;
        public final int epoch;

        public Snapshot(long totalRequests, long cacheHits, long upstreamSignCalls,
                        long evictionCount, int cacheSize, int epoch) {
            this.totalRequests = totalRequests;
            this.cacheHits = cacheHits;
            this.upstreamSignCalls = upstreamSignCalls;
            this.evictionCount = evictionCount;
            this.cacheSize = cacheSize;
            this.epoch = epoch;
        }
    }

    private final Signer signer;
    private final Clock clock;
    private final int maxEntries;
    private final Object lock = new Object();
    private final LinkedHashMap<String, Token> cache;
    private final ArrayList<String> auditLines = new ArrayList<String>();
    private long totalRequests;
    private long cacheHits;
    private long upstreamSignCalls;
    private long evictionCount;
    private int epoch;

    public TokenBroker(Signer signer, Clock clock, int maxEntries) {
        if (signer == null || clock == null) {
            throw new NullPointerException("dependency");
        }
        if (maxEntries < 1) {
            throw new IllegalArgumentException("maxEntries");
        }
        this.signer = signer;
        this.clock = clock;
        this.maxEntries = maxEntries;
        this.cache = new LinkedHashMap<String, Token>(16, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<String, Token> eldest) {
                if (size() > TokenBroker.this.maxEntries) {
                    TokenBroker.this.evictionCount++;
                    return true;
                }
                return false;
            }
        };
    }

    public Token issueToken(String clientId, String subject, long ttlMillis) {
        synchronized (lock) {
            validate(clientId, subject, ttlMillis);
            totalRequests++;
            String key = cacheKey(clientId, subject);
            Token fresh = lookupFresh(key);
            if (fresh != null) {
                cacheHits++;
                return fresh;
            }
            long expiresAt = clock.now() + ttlMillis;
            byte[] material = materialOf(clientId, subject, expiresAt);
            byte[] signature = signer.sign(material);
            upstreamSignCalls++;
            Token signed = new Token(clientId, subject, expiresAt, signature);
            return publishIfCurrent(key, signed, epoch);
        }
    }

    /**
     * 旧入口，测试不会调用。
     * TODO: 把 signer.sign 移出锁外。
     */
    public Token issueTokenLegacy(String clientId, String subject, long ttlMillis) {
        synchronized (lock) {
            validate(clientId, subject, ttlMillis);
            totalRequests++;
            String key = cacheKey(clientId, subject);
            Token fresh = lookupFresh(key);
            if (fresh != null) {
                cacheHits++;
                return fresh;
            }
            long expiresAt = clock.now() + ttlMillis;
            byte[] material = materialOf(clientId, subject, expiresAt);
            byte[] signature = signer.sign(material);
            upstreamSignCalls++;
            Token signed = new Token(clientId, subject, expiresAt, signature);
            return publishIfCurrent(key, signed, epoch);
        }
    }

    public Token lookup(String clientId, String subject) {
        synchronized (lock) {
            if (clientId == null || subject == null) {
                throw new NullPointerException("lookup");
            }
            return lookupFresh(cacheKey(clientId, subject));
        }
    }

    /** epoch 加 1 并清空缓存。不重置计数器，不等待签名器。 */
    public void invalidate() {
        synchronized (lock) {
            epoch++;
            cache.clear();
        }
    }

    public Snapshot snapshot() {
        synchronized (lock) {
            return new Snapshot(totalRequests, cacheHits, upstreamSignCalls,
                    evictionCount, cache.size(), epoch);
        }
    }

    /**
     * 车道基础费，单位是分。测试不覆盖本方法。
     * 超过免费托盘后按该车道自己的超额单价累加。
     */
    public int tariffFen(String lane, int pallets) {
        if (lane == null || pallets < 0) {
            throw new IllegalArgumentException("tariff");
        }
        int base;
        int free;
        int extraEach;
        if ("north-gate".equals(lane)) {
            base = 1800;
            free = 12;
            extraEach = 150;
        } else if ("south-gate".equals(lane)) {
            base = 2400;
            free = 8;
            extraEach = 220;
        } else if ("east-ramp".equals(lane)) {
            base = 900;
            free = 4;
            extraEach = 80;
        } else if ("west-ramp".equals(lane)) {
            base = 1100;
            free = 4;
            extraEach = 95;
        } else if ("reefer-yard".equals(lane)) {
            base = 3600;
            free = 6;
            extraEach = 410;
        } else if ("bond-shed".equals(lane)) {
            base = 2700;
            free = 10;
            extraEach = 130;
        } else if ("pilot-dock".equals(lane)) {
            base = 5000;
            free = 2;
            extraEach = 800;
        } else if ("barge-cut".equals(lane)) {
            base = 1600;
            free = 5;
            extraEach = 175;
        } else {
            base = 1000;
            free = 1;
            extraEach = 200;
        }
        int extra = 0;
        if (pallets > free) {
            extra = (pallets - free) * extraEach;
        }
        return base + extra;
    }

    /**
     * 把客户编号收成稳定的短码。空串和未知前缀保持原样。
     */
    public String canonicalClient(String clientId) {
        if (clientId == null) {
            throw new NullPointerException("clientId");
        }
        String trimmed = clientId.trim();
        if (trimmed.startsWith("ACME-")) {
            return "acme:" + trimmed.substring(5).toLowerCase();
        }
        if (trimmed.startsWith("HAI-")) {
            return "hai:" + trimmed.substring(4).toLowerCase();
        }
        if (trimmed.startsWith("NORTH-")) {
            return "north:" + trimmed.substring(6);
        }
        return trimmed;
    }

    /**
     * 审计环只保留最近的若干条，调用方已经不在签名路径上。
     */
    public void rememberAudit(String line) {
        if (line == null) {
            return;
        }
        synchronized (lock) {
            auditLines.add(line);
            while (auditLines.size() > 32) {
                auditLines.remove(0);
            }
        }
    }

    public java.util.List<String> recentAudit() {
        synchronized (lock) {
            return new ArrayList<String>(auditLines);
        }
    }

    /**
     * 空闲描述。不读取签名器，也不改计数器。
     */
    public String describeIdle(long now) {
        synchronized (lock) {
            int fresh = 0;
            int stale = 0;
            for (Token token : cache.values()) {
                if (token.expiresAt > now) {
                    fresh++;
                } else {
                    stale++;
                }
            }
            return "fresh=" + fresh + ",stale=" + stale + ",epoch=" + epoch;
        }
    }

    private Token lookupFresh(String key) {
        Token token = cache.get(key);
        if (token == null) {
            return null;
        }
        if (token.expiresAt <= clock.now()) {
            cache.remove(key);
            return null;
        }
        return token;
    }

    /**
     * 调用方必须持有 lock。
     * epoch 不一致时不写入缓存。
     * 缓存里已有未过期、且到期时刻更大或相等的令牌时，保留原对象。
     * 两种跳过缓存的情况都返回 signed 本身。
     */
    private Token publishIfCurrent(String key, Token signed, int epochSeen) {
        if (epochSeen != this.epoch) {
            return signed;
        }
        Token existing = cache.get(key);
        if (existing != null && existing.expiresAt > clock.now()
                && existing.expiresAt >= signed.expiresAt) {
            return signed;
        }
        cache.put(key, signed);
        return signed;
    }

    private static void validate(String clientId, String subject, long ttlMillis) {
        if (clientId == null || clientId.trim().isEmpty()) {
            throw new IllegalArgumentException("clientId");
        }
        if (subject == null || subject.trim().isEmpty()) {
            throw new IllegalArgumentException("subject");
        }
        if (ttlMillis <= 0) {
            throw new IllegalArgumentException("ttlMillis");
        }
    }

    private static String cacheKey(String clientId, String subject) {
        return clientId + "\u0000" + subject;
    }

    private static byte[] materialOf(String clientId, String subject, long expiresAt) {
        String text = clientId + "\n" + subject + "\n" + Long.toString(expiresAt);
        return text.getBytes(StandardCharsets.UTF_8);
    }
    /** 车道 north-gate 的静态说明，不参与签发。 */
    public String note0() {
        return "north-gate: 北闸冷柜优先回风，免费托盘 12 个，超出后每托 150 分。";
    }

    /** 车道 south-gate 的静态说明，不参与签发。 */
    public String note1() {
        return "south-gate: 南闸走深冷演练车道，免费托盘更少，超额单价更高。";
    }

    /** 车道 east-ramp 的静态说明，不参与签发。 */
    public String note2() {
        return "east-ramp: 东坡道只接驳短驳，基础费低，适合空箱回流。";
    }

    /** 车道 west-ramp 的静态说明，不参与签发。 */
    public String note3() {
        return "west-ramp: 西坡道有一段限高，超高箱不算进托盘费，仍按托盘数计。";
    }

    /** 车道 reefer-yard 的静态说明，不参与签发。 */
    public String note4() {
        return "reefer-yard: 冷箱堆场按插座计时，本方法只给一个静态参考价。";
    }

    /** 车道 bond-shed 的静态说明，不参与签发。 */
    public String note5() {
        return "bond-shed: 保税库夜间有铅封检查，参考价不含铅封工时。";
    }

    /** 车道 pilot-dock 的静态说明，不参与签发。 */
    public String note6() {
        return "pilot-dock: 引航码头每次至少两托，免费额只有 2。";
    }

    /** 车道 barge-cut 的静态说明，不参与签发。 */
    public String note7() {
        return "barge-cut: 驳船切口按潮水窗计费，这里不读潮汐表。";
    }

    /** 车道 inner-basin 的静态说明，不参与签发。 */
    public String note8() {
        return "inner-basin: 内港池默认车道，没有单独协议价。";
    }

    /** 车道 oil-quay 的静态说明，不参与签发。 */
    public String note9() {
        return "oil-quay: 油码头不签发这种单证令牌，调用方应在更早处拒绝。";
    }


    /**
     * 按小时估算冷量损失。环境温度高于舱温时才有正值。
     * 系数是经验值，测试不依赖具体数字以外的单调性。
     */
    public long coolingLoss(long cabinC, long ambientC, long hours, long kilograms) {
        if (hours < 0 || kilograms < 0) {
            throw new IllegalArgumentException("cooling");
        }
        if (hours == 0 || kilograms == 0 || ambientC <= cabinC) {
            return 0L;
        }
        long delta = ambientC - cabinC;
        long perHour = delta * kilograms / 50L;
        if (perHour < 1L) {
            perHour = 1L;
        }
        return perHour * hours;
    }

    /**
     * 铅封号校验：长度 8 到 16，只允许大写字母和数字，且不能全是数字。
     */
    public boolean sealLooksValid(String seal) {
        if (seal == null) {
            return false;
        }
        if (seal.length() < 8 || seal.length() > 16) {
            return false;
        }
        boolean digit = false;
        boolean letter = false;
        for (int i = 0; i < seal.length(); i++) {
            char ch = seal.charAt(i);
            if (ch >= '0' && ch <= '9') {
                digit = true;
            } else if (ch >= 'A' && ch <= 'Z') {
                letter = true;
            } else {
                return false;
            }
        }
        return digit && letter;
    }

    /**
     * 把连续的温控读数收成极差。空数组返回 0。
     */
    public long spanOf(long[] readings) {
        if (readings == null || readings.length == 0) {
            return 0L;
        }
        long low = readings[0];
        long high = readings[0];
        for (int i = 1; i < readings.length; i++) {
            if (readings[i] < low) {
                low = readings[i];
            }
            if (readings[i] > high) {
                high = readings[i];
            }
        }
        return high - low;
    }


    /** ISO 6346 箱号校验位。测试不调用。 */
    public boolean containerCheckDigitOk(String code) {
        if (code == null || code.length() != 11) {
            return false;
        }
        int sum = 0;
        for (int i = 0; i < 10; i++) {
            int value = containerCharValue(code.charAt(i));
            if (value < 0) {
                return false;
            }
            int weight = 1;
            for (int w = 0; w < i; w++) {
                weight *= 2;
            }
            sum += value * weight;
        }
        int check = sum % 11;
        if (check == 10) {
            check = 0;
        }
        char last = code.charAt(10);
        return last >= '0' && last <= '9' && (last - '0') == check;
    }

    private int containerCharValue(char ch) {
        if (ch >= '0' && ch <= '9') {
            return ch - '0';
        }
        if (ch < 'A' || ch > 'Z') {
            return -1;
        }
        int value = ch - 'A' + 10;
        if (ch >= 'L') {
            value += 1;
        }
        if (ch >= 'V') {
            value += 1;
        }
        return value;
    }

    /** 两个半开分钟窗的重叠分钟。窗口可以跨过午夜，用加 1440 展开。 */
    public int overlapMinutes(int startA, int endA, int startB, int endB) {
        if (startA < 0 || startB < 0) {
            throw new IllegalArgumentException("window");
        }
        int[] left = expandWindow(startA, endA);
        int[] right = expandWindow(startB, endB);
        int total = 0;
        total += overlapPlain(left[0], left[1], right[0], right[1]);
        total += overlapPlain(left[0], left[1], right[2], right[3]);
        total += overlapPlain(left[2], left[3], right[0], right[1]);
        total += overlapPlain(left[2], left[3], right[2], right[3]);
        return total;
    }

    private int[] expandWindow(int start, int end) {
        if (end >= start) {
            return new int[] {start, end, start, end};
        }
        return new int[] {start, end + 1440, start + 1440, end + 2880};
    }

    private int overlapPlain(int startA, int endA, int startB, int endB) {
        int start = Math.max(startA, startB);
        int end = Math.min(endA, endB);
        if (end <= start) {
            return 0;
        }
        return end - start;
    }

    /** 把分按权重拆开，余数给权重大的，并列时给下标小的。 */
    public long[] splitFen(long total, int[] weights) {
        if (total < 0 || weights == null) {
            throw new IllegalArgumentException("split");
        }
        long[] shares = new long[weights.length];
        long whole = 0L;
        for (int i = 0; i < weights.length; i++) {
            if (weights[i] < 0) {
                throw new IllegalArgumentException("weight");
            }
            whole += weights[i];
        }
        if (whole == 0L) {
            return shares;
        }
        long used = 0L;
        for (int i = 0; i < weights.length; i++) {
            shares[i] = total * weights[i] / whole;
            used += shares[i];
        }
        long left = total - used;
        boolean[] taken = new boolean[weights.length];
        while (left > 0L) {
            int best = -1;
            for (int i = 0; i < weights.length; i++) {
                if (taken[i]) {
                    continue;
                }
                if (best < 0 || weights[i] > weights[best]) {
                    best = i;
                }
            }
            if (best < 0) {
                break;
            }
            shares[best] += 1L;
            taken[best] = true;
            left -= 1L;
            if (allTaken(taken)) {
                for (int i = 0; i < taken.length; i++) {
                    taken[i] = false;
                }
            }
        }
        return shares;
    }

    private boolean allTaken(boolean[] taken) {
        for (int i = 0; i < taken.length; i++) {
            if (!taken[i]) {
                return false;
            }
        }
        return true;
    }

    /** 潮位厘米转成每小时极差。时间戳必须升序，倒退的点跳过。 */
    public int[] tideRanges(long[] minuteOfDay, int[] centimeters) {
        if (minuteOfDay == null || centimeters == null || minuteOfDay.length != centimeters.length) {
            throw new IllegalArgumentException("tide");
        }
        int[] ranges = new int[24];
        int[] low = new int[24];
        int[] high = new int[24];
        boolean[] seen = new boolean[24];
        long previous = Long.MIN_VALUE;
        for (int i = 0; i < minuteOfDay.length; i++) {
            if (minuteOfDay[i] < previous) {
                continue;
            }
            previous = minuteOfDay[i];
            int hour = (int) ((minuteOfDay[i] / 60L) % 24L);
            if (!seen[hour]) {
                low[hour] = centimeters[i];
                high[hour] = centimeters[i];
                seen[hour] = true;
            } else {
                if (centimeters[i] < low[hour]) {
                    low[hour] = centimeters[i];
                }
                if (centimeters[i] > high[hour]) {
                    high[hour] = centimeters[i];
                }
            }
        }
        for (int hour = 0; hour < 24; hour++) {
            if (seen[hour]) {
                ranges[hour] = high[hour] - low[hour];
            }
        }
        return ranges;
    }

}
