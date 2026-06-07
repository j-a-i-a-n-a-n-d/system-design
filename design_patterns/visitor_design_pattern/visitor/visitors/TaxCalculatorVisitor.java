package visitor.visitors;

import visitor.elements.Book;
import visitor.elements.Electronics;
import visitor.elements.Grocery;

/**
 * Concrete Visitor 1: TaxCalculatorVisitor
 *
 * Computes the tax for each item type using different rates:
 * - Books : 5% (educational benefit)
 * - Electronics : 18% (standard GST slab)
 * - Grocery : 0% (essential goods, tax-exempt)
 *
 * None of the element classes need to be modified to add this behaviour.
 */
public class TaxCalculatorVisitor implements ShopVisitor {

    private double totalTax = 0;

    @Override
    public void visit(Book book) {
        double tax = book.getPrice() * 0.05;
        totalTax += tax;
        System.out.printf("  [Tax] Book      %-30s  price: $%7.2f  tax @  5%% = $%.2f%n",
                "\"" + book.getTitle() + "\"", book.getPrice(), tax);
    }

    @Override
    public void visit(Electronics electronics) {
        double tax = electronics.getPrice() * 0.18;
        totalTax += tax;
        System.out.printf("  [Tax] Electro   %-30s  price: $%7.2f  tax @ 18%% = $%.2f%n",
                electronics.getName(), electronics.getPrice(), tax);
    }

    @Override
    public void visit(Grocery grocery) {
        double tax = 0; // essential goods are tax-exempt
        System.out.printf("  [Tax] Grocery   %-30s  price: $%7.2f  tax @  0%% = $%.2f  (exempt)%n",
                grocery.getName(), grocery.getPrice(), tax);
    }

    public double getTotalTax() {
        return totalTax;
    }
}
