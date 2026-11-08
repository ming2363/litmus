package com.litmus.order;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 订单校验结果，包含通过标志、错误码列表与描述信息列表。
 */
public class ValidationResult {
    private final boolean valid;
    private final List<String> errorCodes;
    private final List<String> messages;

    public ValidationResult(List<String> errorCodes, List<String> messages) {
        this.errorCodes = Collections.unmodifiableList(new ArrayList<>(errorCodes));
        this.messages = Collections.unmodifiableList(new ArrayList<>(messages));
        this.valid = this.errorCodes.isEmpty();
    }

    public boolean isValid() {
        return valid;
    }

    public List<String> getErrorCodes() {
        return errorCodes;
    }

    public List<String> getMessages() {
        return messages;
    }
}
