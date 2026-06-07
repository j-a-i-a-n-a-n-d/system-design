package design_patterns.singleton_design_pattern.singleton;

import java.io.Serializable;

/**
 * 5. Bill Pugh Singleton (Static Inner Class Helper).
 * Leverages the JVM class loader mechanism for thread-safe lazy-loading.
 * The inner helper class (Holder) is loaded only when getInstance() is invoked.
 */
public class BillPughSingleton implements Serializable {
    private static final long serialVersionUID = 1L;

    private BillPughSingleton() {
    }

    private static class Holder {
        private static final BillPughSingleton INSTANCE = new BillPughSingleton();
    }

    public static BillPughSingleton getInstance() {
        return Holder.INSTANCE;
    }
}
