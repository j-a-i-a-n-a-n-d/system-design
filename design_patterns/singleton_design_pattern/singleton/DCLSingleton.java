package design_patterns.singleton_design_pattern.singleton;

import java.io.Serializable;

/**
 * 3. Double-Checked Locking (DCL) Singleton.
 * Uses a volatile variable and synchronized block to guarantee thread safety
 * while avoiding the synchronized method performance penalty after initialization.
 */
public class DCLSingleton implements Serializable {
    private static final long serialVersionUID = 1L;

    // volatile keyword is critical to prevent JVM instruction reordering
    private static volatile DCLSingleton instance;

    // Private constructor to prevent instantiation
    private DCLSingleton() {
    }

    public static DCLSingleton getInstance() {
        // First check (no synchronization overhead for subsequent calls)
        if (instance == null) {
            synchronized (DCLSingleton.class) {
                // Second check (to ensure only one thread creates the instance)
                if (instance == null) {
                    instance = new DCLSingleton();
                }
            }
        }
        return instance;
    }
}
