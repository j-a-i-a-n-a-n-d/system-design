package _lld_question.atm_machine.state;

/**
 * AuthenticatedState – PIN verified; the user may now withdraw cash or eject.
 *
 * Valid operations : withdrawCash, ejectCard
 */
public class AuthenticatedState implements ATMState {

    private final ATMContext context;

    public AuthenticatedState(ATMContext context) {
        this.context = context;
    }

    @Override
    public void insertCard() throws Exception {
        throw new Exception("[AuthenticatedState] A card is already inserted and authenticated.");
    }

    @Override
    public void ejectCard() throws Exception {
        System.out.println("Card Ejected");
        context.setAccount(null);
        context.setState(context.getIdleState());
    }

    @Override
    public void insertPin(int pin) throws Exception {
        throw new Exception("[AuthenticatedState] Already authenticated. No need to enter PIN again.");
    }

    @Override
    public void authenticate() throws Exception {
        throw new Exception("[AuthenticatedState] Already authenticated.");
    }

    @Override
    public void withdrawCash(int amount) throws Exception {
        context.setState(context.getTransactionState());
        try {
            context.withdrawCash(amount);
        } catch (Exception e) {
            // Transaction failed — roll back to AuthenticatedState so the
            // user can retry or eject their card normally.
            context.setState(context.getAuthenticatedState());
            throw e;  // re-throw so the caller sees the error
        }
    }
}
