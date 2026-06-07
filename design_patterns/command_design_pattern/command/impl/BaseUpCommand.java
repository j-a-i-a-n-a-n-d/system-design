package design_patterns.command_design_pattern.command.impl;

import design_patterns.command_design_pattern.command.Command;
import design_patterns.command_design_pattern.inputs.impl.SpeakerDevice;

public class BaseUpCommand implements Command {

    private SpeakerDevice speakerDevice;

    public BaseUpCommand(SpeakerDevice speakerDevice) {
        this.speakerDevice = speakerDevice;
    }

    @Override
    public void execute() {
        speakerDevice.bassUp();
    }
}
