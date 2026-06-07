package design_patterns.prototype_design_pattern.prototype;

/**
 * Interface declaring the clone operation.
 * Any class implementing this interface must provide an implementation to clone itself.
 */
public interface Prototype {
    Prototype clone();
}
