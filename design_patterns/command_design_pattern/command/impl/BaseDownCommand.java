package design_patterns.command_design_pattern.command.impl;

import design_patterns.command_design_pattern.command.Command;
import design_patterns.command_design_pattern.inputs.impl.SpeakerDevice;

public class BaseDownCommand implements Command {

    private SpeakerDevice speakerDevice;

    public BaseDownCommand(SpeakerDevice speakerDevice) {
        this.speakerDevice = speakerDevice;
    }

    @Override
    public void execute() {
        speakerDevice.bassDown();
    }
}
