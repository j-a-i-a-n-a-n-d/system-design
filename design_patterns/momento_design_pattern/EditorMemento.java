package design_patterns.momento_design_pattern;

public final class EditorMemento {
    private final String content;
    private final int cursorPos;
    private final long timestamp;

    // package-private constructor
    EditorMemento(String content, int cursorPos) {
        this.content = content;
        this.cursorPos = cursorPos;
        this.timestamp = System.currentTimeMillis();
    }

    // only Originator calls these — Caretaker sees only toString()
    String getContent() {
        return content;
    }

    int getCursorPos() {
        return cursorPos;
    }

    @Override
    public String toString() {
        return "Snapshot[cursor=" + cursorPos + ", preview=\"" + content.substring(0, Math.min(10, content.length()))
                + "...\"]";
    }
}
