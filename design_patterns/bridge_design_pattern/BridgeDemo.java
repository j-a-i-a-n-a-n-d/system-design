package design_patterns.bridge_design_pattern;

import design_patterns.bridge_design_pattern.bridge.Circle;
import design_patterns.bridge_design_pattern.bridge.Rectangle;

public class BridgeDemo {
    public static void main(String[] args) {
        Workspace macCircle = new MacWorkspace(new Circle());
        Workspace macRectangle = new MacWorkspace(new Rectangle());
        Workspace winCircle = new WindowsWorkspace(new Circle());
        Workspace winRectangle = new WindowsWorkspace(new Rectangle());

        macCircle.draw();
        macRectangle.draw();
        winCircle.draw();
        winRectangle.draw();
    }
}
