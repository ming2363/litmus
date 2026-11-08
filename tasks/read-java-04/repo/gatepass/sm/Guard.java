package gatepass.sm;

/** 边的守卫。 */
public interface Guard {
    /** 为真时边可以走。 */
    boolean allows();
}
