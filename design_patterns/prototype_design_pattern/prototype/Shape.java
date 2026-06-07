package design_patterns.prototype_design_pattern.prototype;

/**
 * Abstract class representing a generic Shape.
 * It implements Prototype and defines common properties like id and color.
 * It provides a copy constructor for copying basic properties.
 */
public abstract class Shape implements Prototype {
    private String id;
    private String color;

    // Default constructor
    public Shape() {
    }

    // Copy constructor to copy fields from the prototype source
    public Shape(Shape source) {
        if (source != null) {
            this.id = source.id;
            this.color = source.color;
        }
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    @Override
    public abstract Shape clone();

    @Override
    public String toString() {
        return "Shape{id='" + id + "', color='" + color + "'}";
    }
}
