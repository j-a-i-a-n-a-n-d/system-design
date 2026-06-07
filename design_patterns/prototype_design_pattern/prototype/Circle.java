package design_patterns.prototype_design_pattern.prototype;

/**
 * Concrete prototype representing a Circle.
 */
public class Circle extends Shape {
    private int radius;

    // Default constructor
    public Circle() {
    }

    // Copy constructor
    public Circle(Circle source) {
        super(source);
        if (source != null) {
            this.radius = source.radius;
        }
    }

    public int getRadius() {
        return radius;
    }

    public void setRadius(int radius) {
        this.radius = radius;
    }

    // Cloning using the copy constructor
    @Override
    public Circle clone() {
        return new Circle(this);
    }

    @Override
    public String toString() {
        return "Circle{id='" + getId() + "', color='" + getColor() + "', radius=" + radius + "}";
    }
}
