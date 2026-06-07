package design_patterns.singleton_design_pattern.singleton;

/**
 * 4. Enum Singleton.
 * Best practice implementation as recommended by Joshua Bloch.
 * Provides implicit thread safety, lazy initialization, reflection safety, and serialization safety.
 */
public enum EnumSingleton {
    INSTANCE;

    private String value;

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public void doSomething() {
        System.out.println("Enum Singleton is doing something. Value: " + value);
    }
}
