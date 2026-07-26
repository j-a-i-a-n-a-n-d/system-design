package _lld_question.atm_machine.state.cor.impl;

import java.util.Map;

import _lld_question.atm_machine.cash_inventory.CashInventory;
import _lld_question.atm_machine.cash_inventory.NoteDenomination;
import _lld_question.atm_machine.state.cor.CashHandler;

public class FIFTYcashHandler extends CashHandler {

    private static final int DENOMINATION = 50;

    @Override
    public void dispenseCash(int amount, CashInventory cashInventory, Map<String, Integer> dispensedNotes) {
        int notesNeeded = amount / DENOMINATION;

        if (notesNeeded > 0) {
            int notesAvailable = cashInventory.getCurrentInventory()
                    .getOrDefault(NoteDenomination.FIFTY, 0);

            // Use only as many notes as are available
            int notesToDispense = Math.min(notesNeeded, notesAvailable);

            if (notesToDispense > 0) {
                cashInventory.reduceNotes(NoteDenomination.FIFTY, notesToDispense);
                dispensedNotes.put("50", notesToDispense);
                amount -= notesToDispense * DENOMINATION;
            }
            // If notesAvailable == 0 the full amount falls through to the next handler
        }

        // FIFTYcashHandler is the end of the chain.
        // If amount still > 0 here, the ATM cannot fully service the request.
        if (amount > 0) {
            System.err.println("[FIFTYcashHandler] Cannot dispense remaining ₹" + amount
                    + " — insufficient notes across all denominations.");
        }
    }
}
