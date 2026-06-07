package factory.impl;

import factory.Shape;

public class Circle implements Shape {

    @Override
    public void draw() {
        System.out.println("Drawing a Circle.");
    }
}
