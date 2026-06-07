import java.util.LinkedList;
import java.util.Queue;

public class SlidingWindowLogRateLimiter {
    private final int capacity;
    private final int windowSizeInMillis;
    private final Queue<Long> requestTimestamps;

    public SlidingWindowLogRateLimiter(int capacity, int windowSizeInMillis) {
        this.capacity = capacity;
        this.windowSizeInMillis = windowSizeInMillis;
        this.requestTimestamps = new LinkedList<>();
    }
    // Sliding Window Log: Never resets. It always looks back exactly X minutes from
    // the current second. It perfectly tracks traffic, but the watch-checking takes
    // more memory and effort.

    public synchronized boolean tryAcquire() {
        long now = System.currentTimeMillis();
        // Remove timestamps that are outside the sliding window
        while (!requestTimestamps.isEmpty() && requestTimestamps.peek() <= now - windowSizeInMillis) {
            requestTimestamps.poll();
        }
        // Check if we can add a new request
        if (requestTimestamps.size() < capacity) {
            requestTimestamps.offer(now);
            return true;
        }
        return false;
    }

    public static void main(String[] args) throws InterruptedException {
        // Create a rate limiter: Capacity = 5, Window Size = 1000ms (1 second)
        SlidingWindowLogRateLimiter rateLimiter = new SlidingWindowLogRateLimiter(5, 1000);
        System.out.println("--- Starting Sliding Window Log Test ---");
        System.out.println("Capacity: 5 | Window Size: 1 second\n");
        // Send 3 requests quickly. All should pass.
        for (int i = 1; i <= 3; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
        // Send 3 more requests quickly. The 6th request should be denied as we've hit
        // the limit of 5 for this window.
        for (int i = 4; i <= 6; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
        System.out.println("\nWaiting for 500ms for some requests to fall out of the window...");
        Thread.sleep(500); // Wait 500ms. The first 3 requests should now be outside the window.
        // Send 3 more requests. All should pass as we are in a new window.
        for (int i = 7; i <= 9; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
    }
}