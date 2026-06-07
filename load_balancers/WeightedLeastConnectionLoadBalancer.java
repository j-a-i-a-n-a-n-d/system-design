import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class WeightedLeastConnectionLoadBalancer {
    private final Map<String, ServerInfo> servers = new ConcurrentHashMap<>();

    private static class ServerInfo {
        final int weight;
        final AtomicInteger activeConnections;

        ServerInfo(int weight) {
            this.weight = weight;
            this.activeConnections = new AtomicInteger(0);
        }
    }

    public void addServer(String server, int weight) {
        servers.put(server, new ServerInfo(weight));
    }

    public void removeServer(String server) {
        servers.remove(server);
    }

    public String getNextServer() {
        if (servers.isEmpty()) {
            return null;
        }

        String bestServer = null;
        double minScore = Double.MAX_VALUE;

        for (Map.Entry<String, ServerInfo> entry : servers.entrySet()) {
            ServerInfo info = entry.getValue();
            // Score = activeConnections / weight. Lower score is better.
            double score = (double) info.activeConnections.get() / info.weight;
            
            if (score < minScore) {
                minScore = score;
                bestServer = entry.getKey();
            }
        }

        if (bestServer != null) {
            servers.get(bestServer).activeConnections.incrementAndGet();
        }

        return bestServer;
    }

    public void releaseConnection(String server) {
        ServerInfo info = servers.get(server);
        if (info != null && info.activeConnections.get() > 0) {
            info.activeConnections.decrementAndGet();
        }
    }

    public static void main(String[] args) {
        WeightedLeastConnectionLoadBalancer lb = new WeightedLeastConnectionLoadBalancer();
        
        // Server-A is twice as powerful as Server-B
        lb.addServer("Server-A", 2);
        lb.addServer("Server-B", 1);

        System.out.println("--- Selecting Servers (Weighted) ---");
        // Request 1 -> A (Score 0/2 vs 0/1)
        System.out.println("Request 1 -> " + lb.getNextServer());
        // Request 2 -> A (Score 1/2 vs 0/1, 0.5 < 1.0)
        System.out.println("Request 2 -> " + lb.getNextServer());
        // Request 3 -> B (Score 2/2 vs 0/1, 1.0 = 1.0, implementation picks B)
        System.out.println("Request 3 -> " + lb.getNextServer());
        
        System.out.println("\n--- Server connections check ---");
        System.out.println("Server A connections: " + lb.servers.get("Server-A").activeConnections.get());
        System.out.println("Server B connections: " + lb.servers.get("Server-B").activeConnections.get());
    }
}
