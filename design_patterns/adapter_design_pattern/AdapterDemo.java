
import thirdparty.StripeService;

public class AdapterDemo {
    public static void main() {
        System.out.println("--- Using Expected Target Interface (PayPal) ---");
        // We can use PayPal directly because it implements PaymentGateway
        PaymentGateway paypal = new PayPalGateway();
        paypal.processPayment("USER123", 50.0);

        System.out.println("\n--- Using Incompatible Service via Adapter (Stripe) ---");
        // We want to use Stripe, but it has a different interface (StripeService)
        StripeService stripeService = new StripeService();

        // Use the adapter to make StripeService compatible with PaymentGateway
        PaymentGateway stripeAdapter = new StripeAdapter(stripeService);
        stripeAdapter.processPayment("USER456", 75.0);
    }
}
