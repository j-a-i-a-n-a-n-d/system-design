package design_patterns.prototype_design_pattern.prototype;

import java.util.HashMap;
import java.util.Map;

/**
 * ShapeRegistry acts as the Prototype Registry (or Prototype Manager).
 * It caches set of pre-built prototype shape objects and returns cloned copies to client requests.
 */
public class ShapeRegistry {
    private final Map<String, Shape> registry = new HashMap<>();

    /**
     * Registers a prototype shape in the registry.
     * @param key The key to associate with the prototype
     * @param shape The prototype shape instance
     */
    public void addPrototype(String key, Shape shape) {
        registry.put(key, shape);
    }

    /**
     * Retrieves a cloned copy of a prototype associated with the key.
     * @param key The key associated with the prototype shape
     * @return A deep/cloned copy of the registered shape prototype, or null if key does not exist.
     */
    public Shape getPrototype(String key) {
        Shape shape = registry.get(key);
        return (shape != null) ? shape.clone() : null;
    }
}
