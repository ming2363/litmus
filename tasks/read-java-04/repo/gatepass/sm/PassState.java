package gatepass.sm;

/** 作业单状态。声明顺序就是答案顺序。 */
public enum PassState {
    DRAFT,
    SUBMITTED,
    APPEAL,
    SCREENING,
    CLEARED,
    HELD,
    INSPECTION,
    QUARANTINE,
    RELEASED,
    LOADING,
    DRAINING,
    SEALED,
    DEPARTED,
    CANCELLED,
    EXPIRED,
    APPEAL_OK,
    APPEAL_DENY,
    ARCHIVED
}
