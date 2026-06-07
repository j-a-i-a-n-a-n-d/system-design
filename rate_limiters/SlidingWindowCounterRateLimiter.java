public class SlidingWindowCounterRateLimiter {
    private final int capacity;
    private final long windowSizeInMillis;

    private long currentWindowStartTime;
    private int currentCount;
    private int previousCount;

    public SlidingWindowCounterRateLimiter(int capacity, long windowSizeInMillis) {
        this.capacity = capacity;
        this.windowSizeInMillis = windowSizeInMillis;
        this.currentWindowStartTime = (System.currentTimeMillis() / windowSizeInMillis) * windowSizeInMillis;
        this.currentCount = 0;
        this.previousCount = 0;
    }

    public synchronized boolean tryAcquire() {
        return tryAcquire(System.currentTimeMillis());
    }

    // Visible for testing so we can simulate specific times (like in your image)
    public synchronized boolean tryAcquire(long now) {
        long currentWindowStart = (now / windowSizeInMillis) * windowSizeInMillis;

        // If time has moved into a new window block
        if (currentWindowStart > currentWindowStartTime) {
            long windowsPassed = (currentWindowStart - currentWindowStartTime) / windowSizeInMillis;
            if (windowsPassed == 1) {
                // Exactly 1 window passed
                previousCount = currentCount;
            } else {
                // Time jumped more than 1 window, old data is irrelevant
                previousCount = 0;
            }
            currentWindowStartTime = currentWindowStart;
            currentCount = 0;
        }

        // Calculate how much of the current window has passed
        double currentWindowElapsedPercentage = (double) (now - currentWindowStartTime) / windowSizeInMillis;

        // The overlap percentage of the previous window is (1 - elapsed percentage)
        // Just like the 70% in your image!
        double previousWindowOverlapPercentage = 1.0 - currentWindowElapsedPercentage;

        // Formula: Estimated requests = (Current Window Requests) + (Previous Window
        // Requests * Overlap Percentage)
        double estimatedTotalRequests = currentCount + (previousCount * previousWindowOverlapPercentage);

        if (estimatedTotalRequests < capacity) {
            currentCount++;
            return true;
        }

        return false;
    }

    public static void main(String[] args) {
        // Let's simulate the EXACT scenario from your image!
        // Rate limit: 5 requests / min.
        SlidingWindowCounterRateLimiter rateLimiter = new SlidingWindowCounterRateLimiter(5, 60000);

        System.out.println("--- Minute 1 (Previous Minute) ---");
        // We simulate sending 5 requests in the very first minute
        long mockTime = (System.currentTimeMillis() / 60000) * 60000;
        for (int i = 1; i <= 5; i++) {
            boolean allowed = rateLimiter.tryAcquire(mockTime);
            System.out.println("Request " + i + " at 0s: " + (allowed ? "Allowed ✅" : "Denied ❌"));
        }

        // Now let's move time to the next minute, 30% into it (as shown in your image)
        // 30% of 60 seconds = 18 seconds elapsed in the Current minute.
        // So the overlap of the Previous minute is exactly 70%.
        mockTime += 60_000 + 18_000;

        System.out.println("\n--- Minute 2 (Current Minute, 30% elapsed) ---");
        System.out.println("Formula: current_count + (previous_count * 0.70)");

        // At this point:
        // previous_count = 5
        // Overlap = 0.70 (meaning 3.5 requests from previous window are considered
        // active)

        System.out.println("Sending Request 6..."); // current_count is 0 -> 0 + 3.5 = 3.5 < 5 (Allowed)
        System.out.println("Is Allowed? " + (rateLimiter.tryAcquire(mockTime) ? "Allowed ✅" : "Denied ❌"));

        System.out.println("Sending Request 7..."); // current_count is 1 -> 1 + 3.5 = 4.5 < 5 (Allowed)
        System.out.println("Is Allowed? " + (rateLimiter.tryAcquire(mockTime) ? "Allowed ✅" : "Denied ❌"));

        System.out.println("Sending Request 8..."); // current_count is 2 -> 2 + 3.5 = 5.5 < 5 (Denied!)
        System.out.println("Is Allowed? " + (rateLimiter.tryAcquire(mockTime) ? "Allowed ✅" : "Denied ❌"));

        //
    }
}
