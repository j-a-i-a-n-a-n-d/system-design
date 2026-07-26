package _lld_question.atm_machine.state;

/**
 * CardInsertedState – a card is in the machine; waiting for PIN + authentication.
 *
 * Valid operations : insertPin, authenticate, ejectCard
 */
public class CardInsertedState implements ATMState {

    private final ATMContext context;

    public CardInsertedState(ATMContext context) {
        this.context = context;
    }

    @Override
    public void insertCard() throws Exception {
        throw new Exception("[CardInsertedState] A card is already inserted. Please eject it first.");
    }

    @Override
    public void ejectCard() throws Exception {
        System.out.println("Card Ejected");
        context.setAccount(null);
        context.setState(context.getIdleState());
    }

    @Override
    public void insertPin(int pin) throws Exception {
        context.getAccount().setPin(pin);
        System.out.println("PIN Entered");
    }

    @Override
    public void authenticate() throws Exception {
        if (!context.getBankService().authenticate(context.getAccount())) {
            throw new Exception("[CardInsertedState] Invalid PIN. Authentication failed.");
        }
        System.out.println("Card Authenticated");
        context.setState(context.getAuthenticatedState());
    }

    @Override
    public void withdrawCash(int amount) throws Exception {
        throw new Exception("[CardInsertedState] Please authenticate before withdrawing cash.");
    }
}
