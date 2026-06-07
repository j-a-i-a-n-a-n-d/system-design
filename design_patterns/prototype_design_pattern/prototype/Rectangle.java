package design_patterns.prototype_design_pattern.prototype;

/**
 * Concrete prototype representing a Rectangle.
 */
public class Rectangle extends Shape {
    private int width;
    private int height;

    // Default constructor
    public Rectangle() {
    }

    // Copy constructor
    public Rectangle(Rectangle source) {
        super(source);
        if (source != null) {
            this.width = source.width;
            this.height = source.height;
        }
    }

    public int getWidth() {
        return width;
    }

    public void setWidth(int width) {
        this.width = width;
    }

    public int getHeight() {
        return height;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    // Cloning using the copy constructor
    @Override
    public Rectangle clone() {
        return new Rectangle(this);
    }

    @Override
    public String toString() {
        return "Rectangle{id='" + getId() + "', color='" + getColor() + "', width=" + width + ", height=" + height + "}";
    }
}
