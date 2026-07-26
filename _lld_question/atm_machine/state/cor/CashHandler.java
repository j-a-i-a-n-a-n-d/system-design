package _lld_question.atm_machine.state.cor;

import java.util.Map;

import _lld_question.atm_machine.cash_inventory.CashInventory;

public abstract class CashHandler {
    protected CashHandler nextHandler;

    public CashHandler setNextHandler(CashHandler nextHandler) {
        this.nextHandler = nextHandler;
        return nextHandler;
    }

    public abstract void dispenseCash(int amount, CashInventory cashInventory, Map<String, Integer> dispensedNotes);

}
