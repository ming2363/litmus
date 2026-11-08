package berthroster;

/** 一个泊位上的当值工人。 */
public final class Worker {
    private final String berthId;
    private boolean released;

    private Worker(String berthId) {
        this.berthId = berthId;
    }

    public static Worker hire(String berthId) {
        return new Worker(berthId);
    }

    public String getBerthId() {
        return berthId;
    }

    public boolean isReleased() {
        return released;
    }

    public void release() {
        released = true;
    }
}
