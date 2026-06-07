package design_patterns.momento_design_pattern;

import java.util.ArrayDeque;
import java.util.Deque;

public class UndoManager {
    private final Deque<EditorMemento> history = new ArrayDeque<>();
    private final Deque<EditorMemento> redoStack = new ArrayDeque<>();
    private final TextEditor editor;

    public UndoManager(TextEditor editor) {
        this.editor = editor;
    }

    public void checkpoint() {
        EditorMemento m = editor.save();
        history.push(m);
        redoStack.clear();
        System.out.println("History size: " + history.size() + " — stored: " + m);
    }

    public void undo() {
        if (history.isEmpty()) {
            System.out.println("Nothing to undo.");
            return;
        }
        EditorMemento current = history.pop();
        redoStack.push(current);
        if (!history.isEmpty()) {
            editor.restore(history.peek());
        }
    }

    public void redo() {
        if (redoStack.isEmpty()) {
            System.out.println("Nothing to redo.");
            return;
        }
        EditorMemento m = redoStack.pop();
        editor.restore(m);
        history.push(m);
    }
}
