package design_patterns.command_design_pattern.inputs.impl;

import design_patterns.command_design_pattern.inputs.Device;

public class SpeakerDevice implements Device {

    @Override
    public void turnOn() {
        System.out.println("Speaker is turning on");
    }

    @Override
    public void turnOff() {
        System.out.println("Speaker is turning off");
    }

    public void bassUp() {
        System.out.println("Speaker bass is increasing");
    }

    public void bassDown() {
        System.out.println("Speaker bass is decreasing");
    }

}
