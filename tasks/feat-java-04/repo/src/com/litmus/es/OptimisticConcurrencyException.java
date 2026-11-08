package com.litmus.es;

/**
 * 乐观并发版本冲突异常。
 */
public class OptimisticConcurrencyException extends RuntimeException {
    public OptimisticConcurrencyException(String message) {
        super(message);
    }
}
