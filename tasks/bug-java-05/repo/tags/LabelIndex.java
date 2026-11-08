package tags;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

/**
 * 只收录通过校验的标签，并按字典序输出。
 */
public final class LabelIndex {

    private final Set<String> labels = new TreeSet<String>();

    public void add(String label) {
        if (!LabelValidator.isValid(label)) {
            throw new IllegalArgumentException("非法标签");
        }
        labels.add(label);
    }

    public boolean contains(String label) {
        return labels.contains(label);
    }

    public int size() {
        return labels.size();
    }

    public List<String> all() {
        return Collections.unmodifiableList(new ArrayList<String>(labels));
    }
}
