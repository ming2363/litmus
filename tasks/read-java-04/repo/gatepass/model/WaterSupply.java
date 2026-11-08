package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 加水记录 */
public final class WaterSupply {
    public final String supplyNo;
    public final int litres;
    public final String point;

    public WaterSupply(String supplyNo, int litres, String point) {
        this.supplyNo = supplyNo;
        this.litres = litres;
        this.point = point;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (supplyNo == null || supplyNo.length() < 2 || supplyNo.length() > 16) {
            errors.add("supplyNo");
        }
        if (litres < 0 || litres > 2000000) {
            errors.add("litres");
        }
        if (point == null || point.trim().isEmpty() || point.trim().length() > 40) {
            errors.add("point");
        }
        return errors;
    }

    public String summary() {
        return "WaterSupply:" + String.valueOf(supplyNo);
    }

    /** 升换吨，向下取整。 */
    public int tonnes() {
        return litres / 1000;
    }

}
