package design_patterns.flyweight_design_pattern;

import design_patterns.flyweight_design_pattern.flyweight.TreeFactory;

public class FlyweightDemo {
    public static void main(String[] args) {
        Forest forest = new Forest();

        // Planting trees (some sharing identical types, others with new types)
        System.out.println("--- Planting Trees ---");
        forest.plantTree(10, 20, "Oak", "Green", "OakTexture_V1");
        forest.plantTree(15, 35, "Oak", "Green", "OakTexture_V1"); // Reused!
        forest.plantTree(50, 70, "Pine", "Dark Green", "PineTexture_V2");
        forest.plantTree(55, 80, "Pine", "Dark Green", "PineTexture_V2"); // Reused!
        forest.plantTree(100, 150, "Oak", "Autumn Yellow", "OakTexture_Yellow");
        forest.plantTree(200, 300, "Oak", "Green", "OakTexture_V1"); // Reused!

        System.out.println("\n--- Drawing Forest ---");
        forest.draw();

        System.out.println("\n--- Summary Statistics ---");
        System.out.println("Total trees planted: " + forest.getTreeCount());
        System.out.println("Unique TreeType objects created: " + TreeFactory.getUniqueTypesCount());
    }
}
