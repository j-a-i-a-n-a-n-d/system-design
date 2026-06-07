package design_patterns.flyweight_design_pattern.flyweight;

public class TreeType {
    private final String name;
    private final String color;
    private final String otherTextureData;

    public TreeType(String name, String color, String otherTextureData) {
        this.name = name;
        this.color = color;
        this.otherTextureData = otherTextureData;
    }

    public void draw(int x, int y) {
        System.out.println("Drawing " + name + " tree of color " + color + " at position (" + x + ", " + y + ")");
    }
}
