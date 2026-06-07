import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

public class WeightedRoundRobinLoadBalancer {
    private final List<String> serverPool;
    private final AtomicInteger currentIndex;

    public WeightedRoundRobinLoadBalancer() {
        this.serverPool = new CopyOnWriteArrayList<>();
        this.currentIndex = new AtomicInteger(0);
    }

    public void addServer(String server, int weight) {
        if (server != null && weight > 0) {
            for (int i = 0; i < weight; i++) {
                serverPool.add(server);
            }
        }
    }

    public void removeServer(String server) {
        if (server != null) {
            serverPool.removeIf(s -> s.equals(server));
        }
    }

    public String getNextServer() {
        if (serverPool.isEmpty()) {
            return null;
        }
        // Get the current index and increment it for the next call.
        // Bitwise AND with Integer.MAX_VALUE handles potential negative overflow.
        int size = serverPool.size();
        int index = (currentIndex.getAndIncrement() & Integer.MAX_VALUE) % size;
        return serverPool.get(index);
    }

    public int getPoolSize() {
        return serverPool.size();
    }

    public static void main(String[] args) {
        WeightedRoundRobinLoadBalancer lb = new WeightedRoundRobinLoadBalancer();
        
        // Server A has 3x weight of Server B
        lb.addServer("Server-A", 3);
        lb.addServer("Server-B", 1);

        System.out.println("Wait Pool Size (Expanded): " + lb.getPoolSize());
        System.out.println("\n--- Initial Rotation (A:3, B:1) ---");
        
        for (int i = 0; i < 8; i++) {
            System.out.println("Request " + (i + 1) + " -> " + lb.getNextServer());
        }

        System.out.println("\n--- Removing Server-A ---");
        lb.removeServer("Server-A");
        
        for (int i = 0; i < 3; i++) {
            System.out.println("Request " + (i + 9) + " -> " + lb.getNextServer());
        }

        System.out.println("\n--- Adding Server-C (weight 2) ---");
        lb.addServer("Server-C", 2);
        
        for (int i = 0; i < 6; i++) {
            System.out.println("Request " + (i + 12) + " -> " + lb.getNextServer());
        }
    }
}
