package _lld_question.atm_machine.state;

import java.util.HashMap;
import java.util.Map;

import _lld_question.atm_machine.cash_inventory.NoteDenomination;
import _lld_question.atm_machine.state.cor.CashHandler;
import _lld_question.atm_machine.state.cor.impl.FIFTYcashHandler;
import _lld_question.atm_machine.state.cor.impl.FIVEHUNDREDScashHandler;
import _lld_question.atm_machine.state.cor.impl.ONEHUNDREDcashHandler;
import _lld_question.atm_machine.state.cor.impl.TWOTHOUSANDScashHandler;

/**
 * TransactionState – a cash-dispensing transaction is in progress.
 *
 * Valid operations : withdrawCash
 * After a successful withdrawal the machine transitions back to
 * AuthenticatedState so the user can make another transaction or eject.
 */
public class TransactionState implements ATMState {

    private final ATMContext context;

    public TransactionState(ATMContext context) {
        this.context = context;
    }

    @Override
    public void insertCard() throws Exception {
        throw new Exception("[TransactionState] Transaction in progress. Cannot insert a card.");
    }

    @Override
    public void ejectCard() throws Exception {
        throw new Exception("[TransactionState] Transaction in progress. Please wait before ejecting.");
    }

    @Override
    public void insertPin(int pin) throws Exception {
        throw new Exception("[TransactionState] Transaction in progress. Cannot enter PIN now.");
    }

    @Override
    public void authenticate() throws Exception {
        throw new Exception("[TransactionState] Transaction in progress. Already authenticated.");
    }

    @Override
    public void withdrawCash(int amount) throws Exception {

        // ── Pre-validation (read-only, no inventory modified) ─────────────────
        // Simulate the chain against current stock. If the full amount cannot be
        // covered, abort immediately — nothing is deducted.
        validateCanDispense(amount);

        // ── Build the Chain-of-Responsibility ────────────────────────────────
        CashHandler handler = new TWOTHOUSANDScashHandler();
        handler.setNextHandler(new FIVEHUNDREDScashHandler())
               .setNextHandler(new ONEHUNDREDcashHandler())
               .setNextHandler(new FIFTYcashHandler());

        // ── Run the chain (inventory IS modified here) ────────────────────────
        Map<String, Integer> dispensedNotes = new HashMap<>();
        handler.dispenseCash(amount, context.getCashInventory(), dispensedNotes);

        int actuallyDispensed = dispensedNotes.entrySet().stream()
                .mapToInt(e -> Integer.parseInt(e.getKey()) * e.getValue())
                .sum();

        context.getBankService().debitMoney(context.getAccount(), actuallyDispensed);

        System.out.println("Dispensed ₹" + actuallyDispensed + " as:");
        dispensedNotes.forEach((denom, count) ->
                System.out.println("  ₹" + denom + " × " + count));
        System.out.println("Remaining Balance : ₹" + context.getAccount().getBalance());

        // ── Return to authenticated state ─────────────────────────────────────
        context.setState(context.getAuthenticatedState());
    }

    /**
     * Read-only simulation: walks through the same greedy algorithm as the CoR
     * chain but only reads from inventory — never modifies it.
     * Throws if the full amount cannot be covered by available denominations.
     */
    private void validateCanDispense(int amount) throws Exception {
        int[] denomValues = {2000, 500, 100, 50};
        Map<NoteDenomination, Integer> stock = context.getCashInventory().getCurrentInventory();
        NoteDenomination[] denomKeys = {
                NoteDenomination.TWOTHOUSANDS,
                NoteDenomination.FIVEHUNDREDS,
                NoteDenomination.ONEHUNDRED,
                NoteDenomination.FIFTY
        };

        int remaining = amount;
        for (int i = 0; i < denomValues.length; i++) {
            int canUse = Math.min(remaining / denomValues[i], stock.getOrDefault(denomKeys[i], 0));
            remaining -= canUse * denomValues[i];
        }

        if (remaining > 0) {
            throw new Exception(
                    "Cannot dispense ₹" + amount + " — ₹" + remaining
                    + " cannot be covered by any available denomination. Transaction aborted.");
        }
    }
}

