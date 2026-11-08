package yardorder.support;

/** 权限位。 */
public final class Acl {
    public static final int READ = 1;
    public static final int WRITE = 2;
    public static final int AUDIT = 4;
    public static final int EXPORT = 8;

    private Acl() {
    }

    public static boolean allows(int granted, int required) {
        return (granted & required) == required;
    }

    public static int grant(int granted, int extra) {
        return granted | extra;
    }

    public static int revoke(int granted, int extra) {
        return granted & ~extra;
    }
}
