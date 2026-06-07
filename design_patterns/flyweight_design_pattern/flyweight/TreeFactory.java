package design_patterns.flyweight_design_pattern.flyweight;

import java.util.HashMap;
import java.util.Map;

public class TreeFactory {
    private static final Map<String, TreeType> treeTypes = new HashMap<>();

    public static TreeType getTreeType(String name, String color, String otherTextureData) {
        String key = name + "_" + color + "_" + otherTextureData;
        TreeType result = treeTypes.get(key);
        if (result == null) {
            result = new TreeType(name, color, otherTextureData);
            treeTypes.put(key, result);
            System.out.println("[Factory] Created new TreeType for: " + name);
        } else {
            System.out.println("[Factory] Reusing existing TreeType for: " + name);
        }
        return result;
    }

    public static int getUniqueTypesCount() {
        return treeTypes.size();
    }
}
