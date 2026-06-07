package observer;

import java.util.ArrayList;
import java.util.List;

public class SecureStock implements Stock {
    private List<Observer> observers = new ArrayList<>();
    private String name;
    private double price;

    public SecureStock(String name, double price) {
        this.name = name;
        this.price = price;
    }

    public void setPrice(double price) {
        this.price = price;
        notifyObservers();
    }

    @Override
    public void registerObserver(Observer o) {
        observers.add(o);
    }

    @Override
    public void removeObserver(Observer o) {
        observers.remove(o);
    }

    @Override
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(name, price);
        }
    }
}
