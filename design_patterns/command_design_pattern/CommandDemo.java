package design_patterns.command_design_pattern;

import design_patterns.command_design_pattern.command.Command;
import design_patterns.command_design_pattern.command.impl.BaseDownCommand;
import design_patterns.command_design_pattern.command.impl.BaseUpCommand;
import design_patterns.command_design_pattern.command.impl.TurnOffComand;
import design_patterns.command_design_pattern.command.impl.TurnOnCommand;
import design_patterns.command_design_pattern.command.impl.VolumeDownCommand;
import design_patterns.command_design_pattern.command.impl.VolumeUpCommand;
import design_patterns.command_design_pattern.inputs.impl.SpeakerDevice;
import design_patterns.command_design_pattern.inputs.impl.TvDevice;

public class CommandDemo {
    public static void main() {

        TvDevice tvDevice = new TvDevice();
        SpeakerDevice speakerDevice = new SpeakerDevice();

        Command turnOnCommand = new TurnOnCommand(tvDevice);
        Command turnOffCommand = new TurnOffComand(tvDevice);
        Command volumeUpCommand = new VolumeUpCommand(tvDevice);
        Command volumeDownCommand = new VolumeDownCommand(tvDevice);
        Command baseUpCommand = new BaseUpCommand(speakerDevice);
        Command baseDownCommand = new BaseDownCommand(speakerDevice);

        Invoker invoker = new Invoker();

        invoker.setCommand(turnOnCommand);
        invoker.pressButton();

        invoker.setCommand(volumeUpCommand);
        invoker.pressButton();

        invoker.setCommand(volumeDownCommand);
        invoker.pressButton();

        invoker.setCommand(baseUpCommand);
        invoker.pressButton();

        invoker.setCommand(turnOffCommand);
        invoker.pressButton();

        invoker.setCommand(baseDownCommand);
        invoker.pressButton();
    }
}
