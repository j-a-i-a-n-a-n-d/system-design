package design_patterns.command_design_pattern.command.impl;

import design_patterns.command_design_pattern.command.Command;
import design_patterns.command_design_pattern.inputs.impl.TvDevice;

public class VolumeDownCommand implements Command {

    private TvDevice tvDevice;

    public VolumeDownCommand(TvDevice tvDevice) {
        this.tvDevice = tvDevice;
    }

    @Override
    public void execute() {
        tvDevice.volumeDown();
    }
}
