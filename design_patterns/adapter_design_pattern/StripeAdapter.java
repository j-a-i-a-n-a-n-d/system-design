import thirdparty.StripeService;

public class StripeAdapter implements PaymentGateway {
    private StripeService stripeService;

    public StripeAdapter(StripeService stripeService) {
        this.stripeService = stripeService;
    }

    @Override
    public void processPayment(String accountId, double amount) {
        // Map the parameters and translate the method call to what the Adaptee expects
        System.out.println("Adapter: Translating 'processPayment' to 'makeCharge'...");
        stripeService.makeCharge(amount, accountId);
    }
}
