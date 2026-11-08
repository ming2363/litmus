package com.litmus.signing;

import java.util.Objects;

/**
 * 不可变已签发令牌。
 */
public final class SignedToken {
    private final String clientId;
    private final String tokenValue;
    private final long issuedAtEpochMs;
    private final long expiresAtEpochMs;

    public SignedToken(String clientId, String tokenValue, long issuedAtEpochMs, long expiresAtEpochMs) {
        this.clientId = Objects.requireNonNull(clientId, "clientId 不能为空");
        this.tokenValue = Objects.requireNonNull(tokenValue, "tokenValue 不能为空");
        this.issuedAtEpochMs = issuedAtEpochMs;
        this.expiresAtEpochMs = expiresAtEpochMs;
    }

    public String clientId() {
        return clientId;
    }

    public String tokenValue() {
        return tokenValue;
    }

    public long issuedAtEpochMs() {
        return issuedAtEpochMs;
    }

    public long expiresAtEpochMs() {
        return expiresAtEpochMs;
    }
}
