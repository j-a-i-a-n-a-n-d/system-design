public class LeakyTokenBucketRateLimiter {
    private final int capacity; // maximum capacity of the bucket
    private final int leakRatePerSecond; // leak rate per second
    private int currentTokens; // current tokens in the bucket
    private long lastLeakTimeMillis; // last time leak occured

    public LeakyTokenBucketRateLimiter(int capacity, int leakRatePerSecond) {
        this.capacity = capacity;
        this.leakRatePerSecond = leakRatePerSecond;
        this.currentTokens = 0; // Bucket starts empty
        this.lastLeakTimeMillis = System.currentTimeMillis();
    }

    public synchronized boolean tryAcquire() { // Tries to add 1 token
        leak(); // First, let tokens leak out
        if (currentTokens < capacity) {
            currentTokens++;
            return true;
        }
        return false;
    }

    private void leak() { // Leaks tokens based on how much time has passed
        long now = System.currentTimeMillis();
        long elapsedTimeInMillis = now - lastLeakTimeMillis;
        long secondsPassed = elapsedTimeInMillis / 1000;
        if (secondsPassed > 0) {
            int tokensToLeak = (int) (secondsPassed * leakRatePerSecond);
            currentTokens = Math.max(0, currentTokens - tokensToLeak); // Tokens cannot go below 0
            lastLeakTimeMillis += (secondsPassed * 1000); // Advance the last leak time
        }
    }

    public static void main(String[] args) throws InterruptedException {
        // Create a rate limiter: Capacity = 5, Leak = 2 tokens per second
        LeakyTokenBucketRateLimiter rateLimiter = new LeakyTokenBucketRateLimiter(5, 2);
        System.out.println("--- Starting Leaky Bucket Test ---");
        System.out.println("Bucket Capacity: 5 | Leak Rate: 2 tokens/sec\n");
        // Add 3 tokens quickly. All should pass.
        for (int i = 1; i <= 6; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
        System.out.println("\nWaiting for 2 seconds to let tokens leak...");
        Thread.sleep(2000); // Wait 2 seconds. 4 tokens should leak (2/sec * 2 sec).
        // Bucket should now be empty.
        // Try 4 requests. All should pass as bucket is empty.
        for (int i = 4; i <= 7; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
    }
}
