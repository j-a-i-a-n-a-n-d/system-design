package design_patterns.bridge_design_pattern;

import design_patterns.bridge_design_pattern.bridge.Shape;

public class MacWorkspace extends Workspace {
    public MacWorkspace(Shape shape) {
        super(shape);
    }

    @Override
    public void draw() {
        System.out.print("On Mac OS - ");
        shape.draw();
    }
}
