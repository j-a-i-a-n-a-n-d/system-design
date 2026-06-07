package visitor.elements;

import visitor.visitors.ShopVisitor;

/**
 * Concrete Element: Grocery
 * Groceries have a name, price, and a perishable flag.
 * Calling accept() dispatches to visitor.visit(Grocery).
 */
public class Grocery implements ShopElement {

    private final String name;
    private final double price;
    private final boolean perishable;

    public Grocery(String name, double price, boolean perishable) {
        this.name = name;
        this.price = price;
        this.perishable = perishable;
    }

    public String getName() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    public boolean isPerishable() {
        return perishable;
    }

    @Override
    public void accept(ShopVisitor visitor) {
        visitor.visit(this); // double dispatch — visitor knows it's a Grocery
    }
}
