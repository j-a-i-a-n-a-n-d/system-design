package thirdparty;

public class StripeService {
    // Note that the method name and parameter order/types are different from PaymentGateway
    public void makeCharge(double chargeAmount, String customerToken) {
        System.out.println("Charging $" + chargeAmount + " on token " + customerToken + " via Stripe.");
    }
}
