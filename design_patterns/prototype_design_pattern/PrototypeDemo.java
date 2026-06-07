package design_patterns.prototype_design_pattern;

import design_patterns.prototype_design_pattern.prototype.Circle;
import design_patterns.prototype_design_pattern.prototype.Rectangle;
import design_patterns.prototype_design_pattern.prototype.Shape;
import design_patterns.prototype_design_pattern.prototype.ShapeGroup;
import design_patterns.prototype_design_pattern.prototype.ShapeRegistry;

public class PrototypeDemo {
    public static void main(String[] args) {
        System.out.println("=== PART 1: Standard Prototype Design Pattern Demo ===");
        ShapeRegistry registry = new ShapeRegistry();

        Circle greenCircle = new Circle();
        greenCircle.setId("C1");
        greenCircle.setColor("Green");
        greenCircle.setRadius(10);
        registry.addPrototype("GreenCircle", greenCircle);

        Rectangle blueRectangle = new Rectangle();
        blueRectangle.setId("R1");
        blueRectangle.setColor("Blue");
        blueRectangle.setWidth(20);
        blueRectangle.setHeight(30);
        registry.addPrototype("BlueRectangle", blueRectangle);

        System.out.println("Cloning shape prototypes from the registry...");
        Shape clonedCircle1 = registry.getPrototype("GreenCircle");
        Shape clonedCircle2 = registry.getPrototype("GreenCircle");
        Shape clonedRectangle = registry.getPrototype("BlueRectangle");

        System.out.println("Original Green Circle Prototype: " + greenCircle);
        System.out.println("Cloned Circle 1: " + clonedCircle1);
        System.out.println("Cloned Circle 2: " + clonedCircle2);
        System.out.println("Cloned Rectangle: " + clonedRectangle);

        System.out.println("clonedCircle1 != greenCircle: " + (clonedCircle1 != greenCircle)
                + " (Objects are separate memory instances)");
        System.out.println("clonedCircle1 != clonedCircle2: " + (clonedCircle1 != clonedCircle2)
                + " (Every clone operation creates a fresh instance)");
        System.out.println(
                "clonedCircle1 class matches greenCircle: " + (clonedCircle1.getClass() == greenCircle.getClass()));

        if (clonedCircle1 instanceof Circle) {
            Circle circle = (Circle) clonedCircle1;
            circle.setRadius(15);
            circle.setColor("Lime Green");
        }

        System.out.println("Original Green Circle Prototype (should be unchanged): " + greenCircle);
        System.out.println("Cloned Circle 1 (should be modified): " + clonedCircle1);
        System.out.println("Cloned Circle 2 (should be unchanged): " + clonedCircle2);

        System.out.println("\n=== PART 2: Prototype with Lists of Polymorphic Objects (The Savior Scenario) ===");

        ShapeGroup originalGroup = new ShapeGroup("OriginalGroup");
        originalGroup.addShape(greenCircle);
        originalGroup.addShape(blueRectangle);
        System.out.println("Original Shape Group: " + originalGroup);

        ShapeGroup clonedGroup = originalGroup.clone();
        System.out.println("Cloned Shape Group:   " + clonedGroup);

        System.out.println("\n--- Modifying the Cloned Group ---");

        Shape firstShapeInClone = clonedGroup.getShapes().get(0);
        firstShapeInClone.setColor("Purple");

        Circle yellowCircle = new Circle();
        yellowCircle.setId("C2");
        yellowCircle.setColor("Yellow");
        yellowCircle.setRadius(5);
        clonedGroup.addShape(yellowCircle);

        System.out.println("Original Shape Group (should remain completely UNTOUCHED):");
        System.out.println(" -> " + originalGroup);
        System.out.println("Cloned Shape Group (should reflect both modifications):");
        System.out.println(" -> " + clonedGroup);

        System.out.println("\n--- Why Prototype is a Saviour here? ---");
        System.out.println(
                "1. Without Prototype, cloning a List<Shape> would require type inspection (instanceof) and explicit casting:");
        System.out.println("   for (Shape s : list) {");
        System.out.println("       if (s instanceof Circle) copy.add(new Circle((Circle) s));");
        System.out.println("       else if (s instanceof Rectangle) copy.add(new Rectangle((Rectangle) s));");
        System.out.println("       // Violates Open-Closed Principle whenever a new shape type is added!");
        System.out.println("   }");
        System.out.println("2. With Prototype, it's a simple, extensible polymorphic call:");
        System.out.println("   for (Shape s : list) { copy.add(s.clone()); }");
    }
}
