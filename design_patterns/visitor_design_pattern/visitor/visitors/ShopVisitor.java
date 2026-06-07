package visitor.visitors;

import visitor.elements.Book;
import visitor.elements.Electronics;
import visitor.elements.Grocery;

/**
 * Visitor interface: declares one visit() overload per concrete element type.
 *
 * Adding a new operation (e.g. ShippingCostVisitor) means implementing this
 * interface — zero changes to the element classes.
 */
public interface ShopVisitor {
    void visit(Book book);

    void visit(Electronics electronics);

    void visit(Grocery grocery);
}
