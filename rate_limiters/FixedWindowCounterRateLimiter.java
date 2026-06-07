public class FixedWindowCounterRateLimiter {
    private final int capacity; // maximum capacity of the window
    private final int windowSizeInMillis; // size of the window in milliseconds
    private int currentCount; // current count of requests in the window
    private long windowStartTimeMillis; // start time of the current window

    public FixedWindowCounterRateLimiter(int capacity, int windowSizeInMillis) {
        this.capacity = capacity;
        this.windowSizeInMillis = windowSizeInMillis;
        this.currentCount = 0;
        this.windowStartTimeMillis = System.currentTimeMillis();
    }

    public synchronized boolean tryAcquire() {
        long now = System.currentTimeMillis();
        long elapsedTimeInMillis = now - windowStartTimeMillis;
        if (elapsedTimeInMillis >= windowSizeInMillis) {
            // Window has passed, reset the counter and start a new window
            currentCount = 0;
            windowStartTimeMillis = now;
        }
        if (currentCount < capacity) {
            currentCount++;
            return true;
        }
        return false;
    }

    public static void main(String[] args) throws InterruptedException {
        // Create a rate limiter: Capacity = 5, Window Size = 1000ms (1 second)
        FixedWindowCounterRateLimiter rateLimiter = new FixedWindowCounterRateLimiter(5, 1000);
        System.out.println("--- Starting Fixed Window Counter Test ---");
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
        System.out.println("\nWaiting for 1 second for the window to reset...");
        Thread.sleep(1000); // Wait for the window to reset
        // Send 3 more requests. All should pass as we are in a new window.
        for (int i = 7; i <= 9; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
    }
}