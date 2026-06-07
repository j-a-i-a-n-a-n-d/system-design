package visitor.visitors;

import visitor.elements.Book;
import visitor.elements.Electronics;
import visitor.elements.Grocery;

/**
 * Concrete Visitor 2: DiscountVisitor
 *
 * Applies promotional discounts per category:
 * - Books : 10% off (reading promotion)
 * - Electronics : 5% off (weekend sale)
 * - Grocery : 2% off (loyalty discount)
 *
 * A completely new operation added WITHOUT touching any element class.
 */
public class DiscountVisitor implements ShopVisitor {

    private double totalSavings = 0;

    @Override
    public void visit(Book book) {
        double discount = book.getPrice() * 0.10;
        totalSavings += discount;
        System.out.printf("  [Disc] Book      %-30s  price: $%7.2f  discount @ 10%% = $%.2f%n",
                "\"" + book.getTitle() + "\"", book.getPrice(), discount);
    }

    @Override
    public void visit(Electronics electronics) {
        double discount = electronics.getPrice() * 0.05;
        totalSavings += discount;
        System.out.printf("  [Disc] Electro   %-30s  price: $%7.2f  discount @  5%% = $%.2f%n",
                electronics.getName(), electronics.getPrice(), discount);
    }

    @Override
    public void visit(Grocery grocery) {
        double discount = grocery.getPrice() * 0.02;
        totalSavings += discount;
        System.out.printf("  [Disc] Grocery   %-30s  price: $%7.2f  discount @  2%% = $%.2f%n",
                grocery.getName(), grocery.getPrice(), discount);
    }

    public double getTotalSavings() {
        return totalSavings;
    }
}
