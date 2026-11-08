package gatepass.model;

import java.util.ArrayList;
import java.util.List;

/** 系缆记录 */
public final class MooringLine {
    public final String berth;
    public final int count;
    public final int minimum;
    public final String material;

    public MooringLine(String berth, int count, int minimum, String material) {
        this.berth = berth;
        this.count = count;
        this.minimum = minimum;
        this.material = material;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (berth == null || berth.length() < 2 || berth.length() > 16) {
            errors.add("berth");
        }
        if (count < 0 || count > 20) {
            errors.add("count");
        }
        if (minimum < 2 || minimum > 12) {
            errors.add("minimum");
        }
        if (!("wire".equals(material) || "rope".equals(material) || "mixed".equals(material))) {
            errors.add("material");
        }
        return errors;
    }

    public String summary() {
        return "MooringLine:" + String.valueOf(berth);
    }

    /** 根数达到下限。 */
    public boolean enough() {
        return count >= minimum;
    }

}
