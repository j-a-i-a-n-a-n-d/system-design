package design_patterns.bridge_design_pattern.bridge;

public class Circle implements Shape {

    @Override
    public void draw() {
        System.out.println("Drawing Circle from shape");
    }

}
