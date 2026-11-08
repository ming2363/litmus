package pilotage.container;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

import pilotage.billing.BillingGateway;

/** 按环境和优先级选定实现后计算报价，返回分。 */
public final class Selector {
    private Selector() {
    }

    /**
     * 规则：
     * 只保留 profile 与接口名都相同的绑定；
     * conditionKey 不是 null 时，属性值必须恰好是 true，否则丢弃；
     * 剩下的按 priority 升序，再按实现类名升序，取第一条。
     * 然后调用该实现的 quoteFen，不把类名返回给调用方。
     */
    public static int choose(String profile, String interfaceName) throws IOException {
        pilotage.external.HarborClock.sync();
        Map<String, String> props = Props.load(profile);
        List<Binding> ready = new ArrayList<Binding>();
        for (int i = 0; i < ProfileData.BINDINGS.size(); i++) {
            Binding binding = ProfileData.BINDINGS.get(i);
            if (!binding.profile.equals(profile) || !binding.interfaceName.equals(interfaceName)) {
                continue;
            }
            if (binding.conditionKey != null) {
                String value = props.get(binding.conditionKey);
                if (!"true".equals(value)) {
                    continue;
                }
            }
            ready.add(binding);
        }
        if (ready.isEmpty()) {
            throw new IllegalStateException("unbound");
        }
        Collections.sort(ready, new Comparator<Binding>() {
            @Override
            public int compare(Binding left, Binding right) {
                if (left.priority != right.priority) {
                    return left.priority - right.priority;
                }
                return left.implementation.compareTo(right.implementation);
            }
        });
        String className = ready.get(0).implementation;
        try {
            Class<?> type = Class.forName(className);
            Object instance = type.getDeclaredConstructor().newInstance();
            if (!(instance instanceof BillingGateway)) {
                throw new IllegalStateException("unbound");
            }
            return ((BillingGateway) instance).quoteFen("HBR-" + profile);
        } catch (ReflectiveOperationException ex) {
            throw new IllegalStateException("unbound");
        }
    }
}
