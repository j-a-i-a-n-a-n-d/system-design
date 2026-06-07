package design_patterns.momento_design_pattern;

public class TextEditor {
    private String content = "";
    private int cursorPos = 0;

    public void type(String text) {
        content = content.substring(0, cursorPos) + text + content.substring(cursorPos);
        cursorPos += text.length();
    }

    public void delete(int chars) {
        if (cursorPos < chars)
            return;
        content = content.substring(0, cursorPos - chars) + content.substring(cursorPos);
        cursorPos -= chars;
    }

    public void moveCursor(int pos) {
        cursorPos = Math.max(0, Math.min(pos, content.length()));
    }

    // momento design here
    public EditorMemento save() {
        System.out.println("Save");
        return new EditorMemento(content, cursorPos);
    }

    public void restore(EditorMemento m) {
        this.content = m.getContent(); // only Originator reads internals
        this.cursorPos = m.getCursorPos();
        System.out.println("Restored to: " + m);
    }

    public void printState() {
        System.out.println("Content: \"" + content + "\"  cursor: " + cursorPos);
    }
}
