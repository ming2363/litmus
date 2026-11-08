package berthroster.support;

import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

/** 按优先级分配库存。 */
public final class Allocator {
    private Allocator() {
    }

    public static final class Request {
        public final String id;
        public final String sku;
        public final int qty;
        public final int priority;

        public Request(String id, String sku, int qty, int priority) {
            this.id = id;
            this.sku = sku;
            this.qty = qty;
            this.priority = priority;
        }
    }

    public static int[] fulfill(Map<String, Integer> stock, Request[] requests) {
        Map<String, Integer> left = new HashMap<String, Integer>(stock);
        Request[] ordered = Arrays.copyOf(requests, requests.length);
        Arrays.sort(ordered, new Comparator<Request>() {
            @Override
            public int compare(Request leftReq, Request rightReq) {
                if (leftReq.priority != rightReq.priority) {
                    return leftReq.priority - rightReq.priority;
                }
                return leftReq.id.compareTo(rightReq.id);
            }
        });
        int[] granted = new int[ordered.length];
        for (int i = 0; i < ordered.length; i++) {
            Request request = ordered[i];
            int have = left.containsKey(request.sku) ? left.get(request.sku).intValue() : 0;
            int take = Math.min(have, request.qty);
            left.put(request.sku, Integer.valueOf(have - take));
            granted[i] = take;
        }
        return granted;
    }
}
