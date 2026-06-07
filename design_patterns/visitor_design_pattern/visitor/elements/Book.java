package visitor.elements;

import visitor.visitors.ShopVisitor;

/**
 * Concrete Element: Book
 * Books have a price and an author.
 * Calling accept() dispatches to visitor.visit(Book).
 */
public class Book implements ShopElement {

    private final String title;
    private final String author;
    private final double price;

    public Book(String title, String author, double price) {
        this.title = title;
        this.author = author;
        this.price = price;
    }

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public double getPrice() {
        return price;
    }

    @Override
    public void accept(ShopVisitor visitor) {
        visitor.visit(this); // double dispatch — visitor knows it's a Book
    }
}
