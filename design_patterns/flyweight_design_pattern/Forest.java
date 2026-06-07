package design_patterns.flyweight_design_pattern;

import java.util.ArrayList;
import java.util.List;

import design_patterns.flyweight_design_pattern.flyweight.Tree;
import design_patterns.flyweight_design_pattern.flyweight.TreeFactory;
import design_patterns.flyweight_design_pattern.flyweight.TreeType;

public class Forest {
    private final List<Tree> trees = new ArrayList<>();

    public void plantTree(int x, int y, String name, String color, String otherTextureData) {
        TreeType type = TreeFactory.getTreeType(name, color, otherTextureData);
        Tree tree = new Tree(x, y, type);
        trees.add(tree);
    }

    public void draw() {
        for (Tree tree : trees) {
            tree.draw();
        }
    }

    public int getTreeCount() {
        return trees.size();
    }
}
