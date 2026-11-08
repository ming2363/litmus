package gatepass.app;

import gatepass.sm.Machine;

/** 程序入口。外部时钟类不在仓库里。 */
public final class GatepassApp {
    private GatepassApp() {
    }

    public static Machine load() {
        return Machine.build();
    }
}
