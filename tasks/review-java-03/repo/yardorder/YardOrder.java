package yardorder;

import java.util.Objects;

/** 堆场订单。相等要同时看单号和箱区。 */
public final class YardOrder {
    private final String id;
    private String zone;

    public YardOrder(String id, String zone) {
        this.id = id;
        this.zone = zone;
    }

    public String getId() {
        return id;
    }

    public String getZone() {
        return zone;
    }

    /** 把订单改到新箱区并交给存储。存储的是改完后的箱区。 */
    public void relocate(String zone, OrderStore store) {
        zone = ZoneNames.normalize(zone);
        store.save(this.id, this.zone);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (!(obj instanceof YardOrder)) {
            return false;
        }
        YardOrder other = (YardOrder) obj;
        return Objects.equals(id, other.id) && Objects.equals(zone, other.zone);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
