package design_patterns.prototype_design_pattern.prototype;

import java.util.ArrayList;
import java.util.List;

/**
 * Concrete Prototype representing a group of shapes.
 * This class illustrates where the Prototype pattern is a lifesaver.
 * When cloning a ShapeGroup, we must perform a deep copy of the shapes list.
 * Thanks to the Prototype pattern, we can clone each shape polymorphically
 * (shape.clone())
 * without having to know or check its concrete type (Circle, Rectangle, etc.).
 */
public class ShapeGroup implements Prototype {
    private String name;
    private List<Shape> shapes = new ArrayList<>();

    public ShapeGroup(String name) {
        this.name = name;
    }

    public ShapeGroup(ShapeGroup source) {
        if (source != null) {
            this.name = source.name;
            for (Shape shape : source.shapes) {
                // shape.clone() will invoke the correct subclass implementation.
                this.shapes.add(shape.clone());
            }
        }
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void addShape(Shape shape) {
        shapes.add(shape);
    }

    public List<Shape> getShapes() {
        return shapes;
    }

    @Override
    public ShapeGroup clone() {
        return new ShapeGroup(this);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("ShapeGroup{name='").append(name).append("', shapes=[");
        for (int i = 0; i < shapes.size(); i++) {
            sb.append(shapes.get(i));
            if (i < shapes.size() - 1) {
                sb.append(", ");
            }
        }
        sb.append("]}");
        return sb.toString();
    }
}
