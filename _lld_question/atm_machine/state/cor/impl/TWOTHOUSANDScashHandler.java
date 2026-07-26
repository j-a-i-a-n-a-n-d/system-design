package _lld_question.atm_machine.state.cor.impl;

import java.util.Map;

import _lld_question.atm_machine.cash_inventory.CashInventory;
import _lld_question.atm_machine.cash_inventory.NoteDenomination;
import _lld_question.atm_machine.state.cor.CashHandler;

public class TWOTHOUSANDScashHandler extends CashHandler {

    private static final int DENOMINATION = 2000;

    @Override
    public void dispenseCash(int amount, CashInventory cashInventory, Map<String, Integer> dispensedNotes) {
        int notesNeeded = amount / DENOMINATION;

        if (notesNeeded > 0) {
            int notesAvailable = cashInventory.getCurrentInventory()
                    .getOrDefault(NoteDenomination.TWOTHOUSANDS, 0);

            // Use only as many notes as are available
            int notesToDispense = Math.min(notesNeeded, notesAvailable);

            if (notesToDispense > 0) {
                cashInventory.reduceNotes(NoteDenomination.TWOTHOUSANDS, notesToDispense);
                dispensedNotes.put("2000", notesToDispense);
                amount -= notesToDispense * DENOMINATION;
            }
            // If notesAvailable == 0 the full amount falls through to the next handler
        }

        // Pass remaining amount down the chain
        if (amount > 0 && nextHandler != null) {
            nextHandler.dispenseCash(amount, cashInventory, dispensedNotes);
        }
    }
}
