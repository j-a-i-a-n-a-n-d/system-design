package design_patterns.composite_design_pattern;

public class CompositeDemo {
    public static void main(String[] args) {
        // Individual developers & designers (Leaf nodes)
        Developer dev1 = new Developer("Alice", "Senior Developer", 120000);
        Developer dev2 = new Developer("Bob", "Frontend Developer", 85000);
        Designer designer1 = new Designer("Charlie", "UX Designer", 90000);

        // Manager of Development team (Composite node)
        Manager engineeringManager = new Manager("Diana", "Engineering");
        engineeringManager.addEmployee(dev1);
        engineeringManager.addEmployee(dev2);

        // Manager of Design team (Composite node)
        Manager designManager = new Manager("Evan", "Creative & Design");
        designManager.addEmployee(designer1);

        // Grand Manager / Director of whole org (Root Composite node)
        Manager director = new Manager("Fiona", "Product & Engineering Division");
        director.addEmployee(engineeringManager);
        director.addEmployee(designManager);

        // Treating the top-level Manager composite just like any single Employee
        System.out.println("--- Full Division Hierarchy ---");
        director.showDetails();
    }
}
