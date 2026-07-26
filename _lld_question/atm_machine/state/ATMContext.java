package _lld_question.atm_machine.state;

import _lld_question.atm_machine.bank.BankService;
import _lld_question.atm_machine.bank.impl.SBIBankService;
import _lld_question.atm_machine.cash_inventory.CashInventory;
import _lld_question.atm_machine.user.Account;

/**
 * ATMContext – the Context in the State Design Pattern.
 *
 * Holds a reference to the current ATMState and delegates every operation to
 * it.  It also owns the shared data (BankService, Account) that concrete
 * states read and write via the provided getters/setters.
 *
 * SOLID highlights
 * ----------------
 * - OCP : new states can be added without modifying this class.
 * - SRP : this class only manages state transitions and shared data.
 * - DIP : depends on the BankService interface, not a concrete bank.
 */
public class ATMContext {

    private ATMState currentState;

    private final BankService bankService;
    private final CashInventory cashInventory;
    private Account account;

    public ATMContext() {
        this.bankService    = new SBIBankService();
        // Switch bank by changing the line above, e.g. new AXISBankService()
        this.cashInventory  = new CashInventory();
        this.currentState   = new IdleState(this);
    }

    // ── State-transition helpers used by concrete states ──────────────────

    public void setState(ATMState state) {
        this.currentState = state;
    }

    public ATMState getIdleState()         { return new IdleState(this); }
    public ATMState getCardInsertedState() { return new CardInsertedState(this); }
    public ATMState getAuthenticatedState(){ return new AuthenticatedState(this); }
    public ATMState getTransactionState()  { return new TransactionState(this); }

    // ── Shared data accessors ─────────────────────────────────────────────

    public BankService   getBankService()   { return bankService; }
    public CashInventory getCashInventory() { return cashInventory; }

    public Account getAccount()                 { return account; }
    public void    setAccount(Account account)  { this.account = account; }

    // ── Public ATM API delegated to current state ─────────────────────────

    public void insertCard(Account account) throws Exception {
        this.account = account;
        currentState.insertCard();
    }

    public void ejectCard() throws Exception {
        currentState.ejectCard();
    }

    public void insertPin(int pin) throws Exception {
        currentState.insertPin(pin);
    }

    public void authenticate() throws Exception {
        currentState.authenticate();
    }

    public void withdrawCash(int amount) throws Exception {
        currentState.withdrawCash(amount);
    }
}
