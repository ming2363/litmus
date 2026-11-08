package gatestats;

/** 一条过车记录。 */
public final class PassRow {
    public final String plate;
    public final long epochMillis;

    public PassRow(String plate, long epochMillis) {
        this.plate = plate;
        this.epochMillis = epochMillis;
    }
}
