package design_patterns.singleton_design_pattern.singleton;

import java.io.Serializable;

/**
 * 2. Lazy Initialization Singleton.
 * Instance is created only when requested for the first time.
 * Note: This implementation is NOT thread-safe.
 */
public class LazySingleton implements Serializable {
    private static final long serialVersionUID = 1L;

    private static LazySingleton instance;

    // Private constructor to prevent instantiation
    private LazySingleton() {
    }

    public static LazySingleton getInstance() {
        if (instance == null) {
            instance = new LazySingleton();
        }
        return instance;
    }
}
