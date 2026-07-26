package _lld_question.atm_machine.cash_inventory;

import java.util.HashMap;
import java.util.Map;

public class CashInventory {

    private Map<NoteDenomination, Integer> notes = new HashMap<>();

    public CashInventory() {
        notes.put(NoteDenomination.TWOTHOUSANDS, 10);
        notes.put(NoteDenomination.FIVEHUNDREDS, 10);
        notes.put(NoteDenomination.ONEHUNDRED, 10);
        notes.put(NoteDenomination.FIFTY, 10);
    }

    public Map<NoteDenomination, Integer> getCurrentInventory() {
        return notes;
    }

    public Map<NoteDenomination, Integer> reduceNotes(NoteDenomination denomination, int count) {
        notes.put(denomination, notes.get(denomination) - count);
        return notes;
    }

}
