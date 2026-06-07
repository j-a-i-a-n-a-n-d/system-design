import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class LeastConnectionLoadBalancer {
    private final Map<String, AtomicInteger> serverConnections = new ConcurrentHashMap<>();

    public void addServer(String server) {
        serverConnections.putIfAbsent(server, new AtomicInteger(0));
    }

    public void removeServer(String server) {
        serverConnections.remove(server);
    }

    public String getNextServer() {
        if (serverConnections.isEmpty()) {
            return null;
        }

        String bestServer = null;
        int minConnections = Integer.MAX_VALUE;

        for (Map.Entry<String, AtomicInteger> entry : serverConnections.entrySet()) {
            int currentConnections = entry.getValue().get();
            if (currentConnections < minConnections) {
                minConnections = currentConnections;
                bestServer = entry.getKey();
            }
        }

        if (bestServer != null) {
            serverConnections.get(bestServer).incrementAndGet();
        }

        return bestServer;
    }

    /**
     * Decrements the connection count for a server.
     * Should be called when a request is completed.
     */
    public void releaseConnection(String server) {
        AtomicInteger connections = serverConnections.get(server);
        if (connections != null && connections.get() > 0) {
            connections.decrementAndGet();
        }
    }

    public static void main(String[] args) {
        LeastConnectionLoadBalancer lb = new LeastConnectionLoadBalancer();
        lb.addServer("Server-A");
        lb.addServer("Server-B");

        System.out.println("--- Selecting Servers (No Releases) ---");
        System.out.println("Request 1 -> " + lb.getNextServer()); // A
        System.out.println("Request 2 -> " + lb.getNextServer()); // B (since A has 1)
        System.out.println("Request 3 -> " + lb.getNextServer()); // A or B (both have 1)
        
        System.out.println("\n--- Releasing Server-A ---");
        lb.releaseConnection("Server-A");
        lb.releaseConnection("Server-A");

        System.out.println("Request 4 -> " + lb.getNextServer()); // Should be A again
    }
}
