package pilotage.model;

import java.util.ArrayList;
import java.util.List;

/** 闸口小票 */
public final class GateTicket {
    public final String ticketNo;
    public final String plate;
    public final String status;
    public final int axles;

    public GateTicket(String ticketNo, String plate, String status, int axles) {
        this.ticketNo = ticketNo;
        this.plate = plate;
        this.status = status;
        this.axles = axles;
    }

    /** 返回错误字段名，空列表表示通过。 */
    public List<String> validate() {
        List<String> errors = new ArrayList<String>();
        if (ticketNo == null || ticketNo.length() < 2 || ticketNo.length() > 16) {
            errors.add("ticketNo");
        }
        if (plate == null || plate.trim().isEmpty() || plate.trim().length() > 40) {
            errors.add("plate");
        }
        if (!("open".equals(status) || "closed".equals(status) || "void".equals(status))) {
            errors.add("status");
        }
        if (axles < 2 || axles > 8) {
            errors.add("axles");
        }
        return errors;
    }

    public String summary() {
        return "GateTicket:" + String.valueOf(ticketNo);
    }

    /** 未核销。 */
    public boolean openTicket() {
        return "open".equals(status);
    }

}
