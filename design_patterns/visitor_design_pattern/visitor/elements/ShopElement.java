package visitor.elements;

import visitor.visitors.ShopVisitor;

/**
 * Element interface: every shop item must accept a visitor.
 *
 * The accept() method is the key hook — it calls back the visitor
 * with the concrete type (double dispatch), letting the visitor
 * choose the right overload without any instanceof checks.
 */
public interface ShopElement {
    void accept(ShopVisitor visitor);
}
