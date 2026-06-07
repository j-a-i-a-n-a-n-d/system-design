package design_patterns.bridge_design_pattern;

import design_patterns.bridge_design_pattern.bridge.Shape;

public class WindowsWorkspace extends Workspace {
    public WindowsWorkspace(Shape shape) {
        super(shape);
    }

    @Override
    public void draw() {
        System.out.print("On Windows OS - ");
        shape.draw();
    }
}
