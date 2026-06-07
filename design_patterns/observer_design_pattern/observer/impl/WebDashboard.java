package observer.impl;

import observer.Observer;

public class WebDashboard implements Observer {
    @Override
    public void update(String stockName, double price) {
        System.out.println("Web Dashboard: " + stockName + " price changed to $" + price);
    }
}
