package concrete.impl;

import concrete.Coffee;

public class CappuchinoCoffee implements Coffee {
    @Override
    public String getDescription() {
        return "Cappuchino Coffee";
    }

    @Override
    public double getCost() {
        return 10.0;
    }
}
