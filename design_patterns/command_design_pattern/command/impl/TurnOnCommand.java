package design_patterns.command_design_pattern.command.impl;

import design_patterns.command_design_pattern.command.Command;
import design_patterns.command_design_pattern.inputs.Device;

public class TurnOnCommand implements Command {

    private Device device;

    public TurnOnCommand(Device device) {
        this.device = device;
    }

    @Override
    public void execute() {
        device.turnOn();
    }
}
