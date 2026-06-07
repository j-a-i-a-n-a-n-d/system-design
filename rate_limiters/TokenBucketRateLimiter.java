public class TokenBucketRateLimiter {
    private final int capacity; // maxmimum capacity of the bucket
    private final int refillRatePerSecond; // refill rate per second
    private int currentTokens; // current tokens which can be supplied to request
    private long lastRefillTimeMillis; // last time refill occured

    public TokenBucketRateLimiter(int capacity, int refillRatePerSecond) {
        this.capacity = capacity;
        this.refillRatePerSecond = refillRatePerSecond;
        this.currentTokens = capacity;
        this.lastRefillTimeMillis = System.currentTimeMillis();
    }

    public synchronized boolean tryAcquire() { // Tries to take 1 token
        refill();
        if (currentTokens > 0) {
            currentTokens--;
            return true;
        }
        return false;
    }

    private void refill() { // Refills tokens based on how much time has passed
        long now = System.currentTimeMillis();
        long elapsedTimeInMillis = now - lastRefillTimeMillis;
        long secondsPassed = elapsedTimeInMillis / 1000;
        if (secondsPassed > 0) {
            int tokensToAdd = (int) (secondsPassed * refillRatePerSecond);
            currentTokens = Math.min(capacity, currentTokens + tokensToAdd); // Current tokens can never exceed the
                                                                             // capacity
            lastRefillTimeMillis += (secondsPassed * 1000); // Advance the last refill time
        }
    }

    public static void main(String[] args) throws InterruptedException {
        TokenBucketRateLimiter rateLimiter = new TokenBucketRateLimiter(3, 1);
        System.out.println("--- Starting Token Bucket Test ---");
        System.out.println("Bucket Capacity: 3 | Refill Rate: 1 token/sec\n");
        for (int i = 1; i <= 5; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
        System.out.println("\nWaiting for 2 seconds to let the bucket refill...");
        Thread.sleep(2000);
        for (int i = 6; i <= 8; i++) {
            boolean isAllowed = rateLimiter.tryAcquire();
            System.out.println("Request " + i + ": " + (isAllowed ? "Allowed ✅" : "Denied ❌"));
        }
    }
}