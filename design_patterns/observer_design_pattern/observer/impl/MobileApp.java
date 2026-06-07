package observer.impl;

import observer.Observer;

public class MobileApp implements Observer {
    @Override
    public void update(String stockName, double price) {
        System.out.println("Mobile App: " + stockName + " price changed to $" + price);
    }
}
