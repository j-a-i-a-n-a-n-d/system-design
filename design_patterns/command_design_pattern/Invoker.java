package design_patterns.command_design_pattern;

import design_patterns.command_design_pattern.command.Command;

public class Invoker {
    private Command command;

    public void setCommand(Command command) {
        this.command = command;
    }

    public void pressButton() {
        if (command != null) {
            command.execute();
        } else {
            System.out.println("No command assigned");
        }
    }
}
