import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

public class RoundRobinLoadBalancer {
    private final List<String> servers;
    private final AtomicInteger currentIndex;

    public RoundRobinLoadBalancer() {
        this.servers = new CopyOnWriteArrayList<>();
        this.currentIndex = new AtomicInteger(0);
    }

    public RoundRobinLoadBalancer(List<String> initialServers) {
        this.servers = new CopyOnWriteArrayList<>(initialServers);
        this.currentIndex = new AtomicInteger(0);
    }

    public void addServer(String server) {
        if (server != null && !servers.contains(server)) {
            servers.add(server);
        }
    }

    public void removeServer(String server) {
        servers.remove(server);
    }

    public String getNextServer() {
        if (servers.isEmpty()) {
            return null;
        }
        // Get the current index and increment it for the next call.
        // Bitwise AND with Integer.MAX_VALUE ensures the index is non-negative.
        int size = servers.size();
        int index = (currentIndex.getAndIncrement() & Integer.MAX_VALUE) % size;
        return servers.get(index);
    }

    public int getServerCount() {
        return servers.size();
    }

    public static void main(String[] args) {
        RoundRobinLoadBalancer lb = new RoundRobinLoadBalancer();        
        lb.addServer("Server-A");
        lb.addServer("Server-B");
        lb.addServer("Server-C");

        System.out.println("\n--- Initial Rotation (3 servers) ---");
        for (int i = 0; i < 6; i++) {
            System.out.println("Request " + (i + 1) + " routed to: " + lb.getNextServer());
        }

        lb.removeServer("Server-B");
        
        for (int i = 0; i < 4; i++) {
            System.out.println("Request " + (i + 7) + " routed to: " + lb.getNextServer());
        }

        lb.addServer("Server-D");
        
        for (int i = 0; i < 6; i++) {
            System.out.println("Request " + (i + 11) + " routed to: " + lb.getNextServer());
        }
    }
}
