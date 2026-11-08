package com.litmus.signing;

/**
 * 上游签名服务接口（实际场景可能存在较高网络延迟）。
 */
public interface UpstreamSigner {
    SignedToken sign(String clientId, long issuedAtEpochMs);
}
