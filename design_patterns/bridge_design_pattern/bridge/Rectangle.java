package design_patterns.bridge_design_pattern.bridge;

public class Rectangle implements Shape {

    @Override
    public void draw() {
        System.out.println("Drawing Rectangle from Shape");
    }

}
