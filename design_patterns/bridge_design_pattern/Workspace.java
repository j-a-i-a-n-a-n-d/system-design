package design_patterns.bridge_design_pattern;

import design_patterns.bridge_design_pattern.bridge.Shape;

public abstract class Workspace {
    protected Shape shape;

    protected Workspace(Shape shape) {
        this.shape = shape;
    }

    public abstract void draw();
}
