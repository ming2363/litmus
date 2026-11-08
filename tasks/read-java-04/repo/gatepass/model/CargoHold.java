package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 船舱货量 */
public final class CargoHold {
    public final String holdNo;
    public final int capacityT;
    public final int loadedT;
    public final String cargo;

    public CargoHold(String holdNo, int capacityT, int loadedT, String cargo) {
        this.holdNo = holdNo;
        this.capacityT = capacityT;
        this.loadedT = loadedT;
        this.cargo = cargo;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (holdNo == null || holdNo.length() < 2 || holdNo.length() > 16) {
            errors.add("holdNo");
        }
        if (capacityT < 1 || capacityT > 20000) {
            errors.add("capacityT");
        }
        if (loadedT < 0 || loadedT > 20000) {
            errors.add("loadedT");
        }
        if (cargo == null || cargo.trim().isEmpty() || cargo.trim().length() > 40) {
            errors.add("cargo");
        }
        return errors;
    }

    public String summary() {
        return "CargoHold:" + String.valueOf(holdNo);
    }

    /** 剩余吨数不为负。 */
    public int freeTonnes() {
        int left = capacityT - loadedT;
        if (left < 0) {
            return 0;
        }
        return left;
    }

}
