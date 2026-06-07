package design_patterns.singleton_design_pattern.singleton;

import java.io.Serializable;

public class EagerSingleton implements Serializable {
    private static final long serialVersionUID = 1L;

    private static final EagerSingleton INSTANCE = new EagerSingleton();

    // Private constructor to prevent instantiation from other classes
    private EagerSingleton() {
    }

    public static EagerSingleton getInstance() {
        return INSTANCE;
    }
}
