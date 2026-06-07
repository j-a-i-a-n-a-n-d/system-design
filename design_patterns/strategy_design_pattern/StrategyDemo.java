import strategy.impl.CreditCardPayment;
import strategy.impl.PayPalPayment;

public class StrategyDemo {
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        cart.checkout(new CreditCardPayment("John Doe", "1234-5678-9012-3456"), 250);
        cart.checkout(new PayPalPayment("john@example.com"), 100);
        // above is just for clean code the method is anyways public and can be accessed
        new CreditCardPayment("John Doe", "1234-5678-9012-3456").pay(200);

    }
}
