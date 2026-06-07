package concrete.impl;

import concrete.Coffee;

public class LatteCoffee implements Coffee {
    @Override
    public String getDescription() {
        return "Latte Coffee";
    }

    @Override
    public double getCost() {
        return 7.5;
    }
}
