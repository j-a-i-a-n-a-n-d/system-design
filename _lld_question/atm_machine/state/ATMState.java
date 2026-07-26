package _lld_question.atm_machine.state;

/**
 * ATMState – the State interface.
 *
 * Every concrete state (IdleState, CardInsertedState, AuthenticatedState,
 * TransactionState) implements this contract.  The ATMContext delegates every
 * public call to the currently-active state, so each state only needs to
 * implement the operations that are valid for it and throw otherwise.
 */
public interface ATMState {

    void insertCard() throws Exception;

    void ejectCard() throws Exception;

    void insertPin(int pin) throws Exception;

    void authenticate() throws Exception;

    void withdrawCash(int amount) throws Exception;
}
