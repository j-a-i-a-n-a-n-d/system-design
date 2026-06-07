package visitor.elements;

import visitor.visitors.ShopVisitor;

/**
 * Concrete Element: Electronics
 * Electronics have a name, price, and warranty period in years.
 * Calling accept() dispatches to visitor.visit(Electronics).
 */
public class Electronics implements ShopElement {

    private final String name;
    private final double price;
    private final int warrantyYears;

    public Electronics(String name, double price, int warrantyYears) {
        this.name = name;
        this.price = price;
        this.warrantyYears = warrantyYears;
    }

    public String getName() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    public int getWarrantyYears() {
        return warrantyYears;
    }

    @Override
    public void accept(ShopVisitor visitor) {
        visitor.visit(this); // double dispatch — visitor knows it's Electronics
    }
}
