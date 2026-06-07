import strategy.PaymentStrategy;

public class ShoppingCart {

    public void checkout(PaymentStrategy paymentMethod, int amount) {
        paymentMethod.pay(amount);
    }
}
