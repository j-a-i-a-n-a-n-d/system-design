import java.util.SortedMap;
import java.util.TreeMap;

/**
 * CONSISTENT HASHING LOAD BALANCER
 * --------------------------------
 * 
 * 1. THE PROBLEM (Modulo Hashing):
 * Standard "hash(key) % serverCount" causes ~100% of keys to remap
 * when a server is added or removed. This destroys caches.
 * 
 * 2. THE SOLUTION (Consistent Hashing Ring):
 * Both servers and requests are hashed onto a logical "circle" (0 to 2^31-1).
 * A request travels clockwise until it hits the first server.
 * 
 * [Diagram: Basic Ring]
 * (Hash 0)
 * |
 * [S3]--+---[S1] <-- Req (H=10) starts here,
 * \ / travels clockwise to [S1]
 * --[S2]-
 * 
 * 3. VIRTUAL NODES (VNodes):
 * Physical servers aren't perfectly distributed. One server might handle
 * a massive "slice" of the ring (hotspots).
 * We solve this by mapping each physical server to 100+ "virtual points".
 * 
 * [Diagram: Virtual Nodes]
 * [S1-V1] -- [S2-V1] -- [S1-V2] -- [S3-V1]
 * (The ring is now populated with many small points,
 * averaging out the distribution).
 */
public class ConsistentHashLoadBalancer {
    private final SortedMap<Integer, String> ring = new TreeMap<>();
    private final int virtualNodeCount;

    public ConsistentHashLoadBalancer(int virtualNodeCount) {
        this.virtualNodeCount = virtualNodeCount;
    }

    /**
     * Adds a server to the ring by creating multiple virtual nodes.
     */
    public void addServer(String server) {
        for (int i = 0; i < virtualNodeCount; i++) {
            // Using a simple salt to ensure virtual nodes hash differently
            String vNodeName = server + "#VN-" + i;
            ring.put(vNodeName.hashCode(), server);
        }
    }

    /**
     * Removes all virtual nodes associated with the physical server.
     */
    public void removeServer(String server) {
        for (int i = 0; i < virtualNodeCount; i++) {
            String vNodeName = server + "#VN-" + i;
            ring.remove(vNodeName.hashCode());
        }
    }

    /**
     * Routes a request key to the nearest server clockwise on the ring.
     */
    public String getRoute(String key) {
        if (ring.isEmpty()) {
            return null;
        }

        int hash = key.hashCode();

        // Find nodes with hash >= request hash
        SortedMap<Integer, String> tailMap = ring.tailMap(hash);

        // If tailMap is empty, the "next" node is the first one in the TreeMap (wrap
        // around)
        int targetHash = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();

        return ring.get(targetHash);
    }

    public static void main(String[] args) {
        // Initialize with 100 virtual nodes per server for smooth distribution
        ConsistentHashLoadBalancer lb = new ConsistentHashLoadBalancer(100);

        lb.addServer("Server-Alpha");
        lb.addServer("Server-Beta");
        lb.addServer("Server-Gamma");

        System.out.println("--- Distributing 10,000 requests ---");
        java.util.Map<String, Integer> distribution = new java.util.HashMap<>();

        for (int i = 0; i < 10000; i++) {
            String route = lb.getRoute("User-Request-" + i);
            distribution.put(route, distribution.getOrDefault(route, 0) + 1);
        }

        distribution.forEach(
                (server, count) -> System.out.println(server + ": " + count + " requests (" + (count / 100.0) + "%)"));

        System.out.println("\n--- Performance Check: Removing Server-Beta ---");
        lb.removeServer("Server-Beta");

        String sampleKey = "User-Request-42";
        System.out.println("Key [" + sampleKey + "] was on Beta, now on -> " + lb.getRoute(sampleKey));
    }
}
