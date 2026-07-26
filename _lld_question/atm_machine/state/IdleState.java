package _lld_question.atm_machine.state;

/**
 * IdleState – the ATM is waiting for a card to be inserted.
 *
 * Valid operations : insertCard
 * All other operations throw an exception because they are out-of-sequence.
 */
public class IdleState implements ATMState {

    private final ATMContext context;

    public IdleState(ATMContext context) {
        this.context = context;
    }

    @Override
    public void insertCard() throws Exception {
        // Card was already set on the context by ATMContext.insertCard()
        context.setAccount(context.getBankService().getAccount(context.getAccount()));
        System.out.println("Card Inserted");
        context.setState(context.getCardInsertedState());
    }

    @Override
    public void ejectCard() throws Exception {
        throw new Exception("[IdleState] No card to eject. Please insert a card first.");
    }

    @Override
    public void insertPin(int pin) throws Exception {
        throw new Exception("[IdleState] Please insert a card before entering a PIN.");
    }

    @Override
    public void authenticate() throws Exception {
        throw new Exception("[IdleState] Please insert a card before authenticating.");
    }

    @Override
    public void withdrawCash(int amount) throws Exception {
        throw new Exception("[IdleState] Please insert a card and authenticate before withdrawing cash.");
    }
}
