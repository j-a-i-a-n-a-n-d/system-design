public interface PaymentGateway {
    void processPayment(String accountId, double amount);
}
