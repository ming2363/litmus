package holdledger.error;

/** 台账读写失败。 */
public class LedgerIOException extends Exception {
    public LedgerIOException(String message) {
        super(message);
    }
}
