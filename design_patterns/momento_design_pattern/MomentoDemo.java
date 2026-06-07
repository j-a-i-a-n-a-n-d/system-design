package design_patterns.momento_design_pattern;

public class MomentoDemo {
    public static void main(String[] args) {
        TextEditor editor = new TextEditor();
        UndoManager manager = new UndoManager(editor);

        System.out.println("=== Typing ===");
        manager.checkpoint(); // v1: ""
        editor.type("Hello");
        editor.printState();
        manager.checkpoint(); // v2: "Hello"

        editor.type(" World");
        editor.printState();
        manager.checkpoint(); // v3: "Hello World"

        editor.type("!");
        editor.printState();
        manager.checkpoint(); // v4: "Hello World!"

        System.out.println("\n=== Undo 2x ===");
        manager.undo();
        editor.printState(); // back to "Hello World"

        manager.undo();
        editor.printState(); // back to "Hello"

        System.out.println("\n=== Redo 1x ===");
        manager.redo();
        editor.printState(); // forward to "Hello World"

        System.out.println("\n=== New change clears redo ===");
        editor.type(" Java");
        manager.checkpoint(); // v: "Hello World Java"
        manager.redo(); // nothing — redo cleared
        editor.printState();
    }

}
