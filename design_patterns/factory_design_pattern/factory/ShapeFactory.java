package factory;

import factory.impl.Square;
import factory.impl.Circle;

public class ShapeFactory {

    // The factory method to get an object of type Shape
    public Shape getShape(String shapeType) {
        if (shapeType == null) {
            return null;
        }

        if (shapeType.equalsIgnoreCase("CIRCLE")) {
            return new Circle();
        } else if (shapeType.equalsIgnoreCase("SQUARE")) {
            return new Square();
        }

        return null;
    }
}
