import java.util.SortedMap;
import java.util.TreeMap;

/**
 * A very basic example of Consistent Hashing.
 * CONCEPT:
 * - Both nodes (servers) and keys are hashed to the same 360-degree range.
 * - A key is assigned to the "next" node encountered moving clockwise on the
 * ring.
 */
public class BasicConsistentHashing {
    // A TreeMap provides a sorted map, perfectly representing the "ring" order.
    private final SortedMap<Integer, String> ring = new TreeMap<>();

    public void addNode(String node) {
        // Simplest version: Hash the node name and place it on the ring
        Integer hash = node.hashCode();
        ring.put(hash, node);
    }

    public void removeNode(String node) {
        ring.remove(node.hashCode());
    }

    public String getNode(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        int hash = key.hashCode();
        // Find entries whose keys are greater than or equal to the hash
        SortedMap<Integer, String> tailMap = ring.tailMap(hash);
        // Clockwise traversal:
        // 1. If tailMap has entries, the first one is the "next" node.
        // 2. If tailMap is empty, we "wrap around" to the firstKey in the entire ring.
        int targetHash = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();
        return ring.get(targetHash);
    }

    public static void main(String[] args) {
        BasicConsistentHashing ch = new BasicConsistentHashing();

        System.out.println("--- Initializing Ring ---");
        ch.addNode("Node-2");
        ch.addNode("Node-1");
        ch.addNode("Node-3");

        // These keys will consistently map to the same nodes
        String[] keys = { "Data-A", "Data-B", "Data-C", "Data-D", "Data-E" };
        for (String key : keys) {
            System.out.println("Key [" + key + "] maps to -> " + ch.getNode(key));
        }

        System.out.println("\n--- Removing Node-1 ---");
        ch.removeNode("Node-1");
        for (String key : keys) {
            System.out.println("Key [" + key + "] now maps to -> " + ch.getNode(key));
        }
    }
}
