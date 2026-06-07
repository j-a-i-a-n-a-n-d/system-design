package design_patterns.command_design_pattern.inputs.impl;

import design_patterns.command_design_pattern.inputs.Device;

public class TvDevice implements Device {

    @Override
    public void turnOn() {
        System.out.println("TV is turning on");
    }

    @Override
    public void turnOff() {
        System.out.println("TV is turning off");
    }

    public void volumeUp() {
        System.out.println("TV volume is increasing");
    }

    public void volumeDown() {
        System.out.println("TV volume is decreasing");
    }

}
