package pilotage.container;

/** 一条条件绑定。conditionKey 为空表示无条件。 */
public final class Binding {
    public final String profile;
    public final String interfaceName;
    public final String implementation;
    public final int priority;
    public final String conditionKey;

    public Binding(String profile, String interfaceName, String implementation, int priority, String conditionKey) {
        this.profile = profile;
        this.interfaceName = interfaceName;
        this.implementation = implementation;
        this.priority = priority;
        this.conditionKey = conditionKey;
    }
}
