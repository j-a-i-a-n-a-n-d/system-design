public class PayPalGateway implements PaymentGateway {
    @Override
    public void processPayment(String accountId, double amount) {
        System.out.println("Processing payment of $" + amount + " for account " + accountId + " via PayPal.");
    }
}
