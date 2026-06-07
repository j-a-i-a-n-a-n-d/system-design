package factory.impl;

import factory.Shape;

public class Square implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing a Square.");
    }
}
