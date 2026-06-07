import java.util.List;

import visitor.elements.Book;
import visitor.elements.Electronics;
import visitor.elements.Grocery;
import visitor.elements.ShopElement;
import visitor.visitors.DiscountVisitor;
import visitor.visitors.TaxCalculatorVisitor;

public class VisitorDemo {
    public static void main() {

        List<ShopElement> cart = List.of(
                new Book("Clean Code", "Robert C. Martin", 45.00),
                new Book("Design Patterns", "Gang of Four", 55.00),
                new Electronics("MacBook Pro", 1999.00, 3),
                new Electronics("Sony WH-1000XM5 Headphones", 349.00, 2),
                new Grocery("Organic Whole Milk", 3.50, true),
                new Grocery("Sourdough Bread", 4.20, true));

        System.out.println("TAX CALCULATION VISITOR");
        TaxCalculatorVisitor taxVisitor = new TaxCalculatorVisitor();
        for (ShopElement item : cart) {
            item.accept(taxVisitor);
        }
        System.out.printf("%nTotal tax payable: $%.2f%n", taxVisitor.getTotalTax());

        System.out.println("DISCOUNT VISITOR");
        DiscountVisitor discountVisitor = new DiscountVisitor();
        for (ShopElement item : cart) {
            item.accept(discountVisitor);
        }
        System.out.printf("%n  ► Total savings     : $%.2f%n", discountVisitor.getTotalSavings());
    }
}
