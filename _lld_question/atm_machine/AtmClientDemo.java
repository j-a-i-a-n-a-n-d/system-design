package _lld_question.atm_machine;

import _lld_question.atm_machine.state.ATMContext;
import _lld_question.atm_machine.user.Account;

public class AtmClientDemo {
    public static void main(String[] args) throws Exception {

        // Account starts with ₹5000 balance
        Account account = new Account("1234567890", "1234567890", 5000, 1111);
        ATMContext atm = new ATMContext();

        // ── Happy path: withdraw ₹2650 ────────────────────────────────────────
        // CoR: 1×₹2000 + 1×₹500 + 1×₹100 + 1×₹50
        atm.insertCard(account);
        atm.insertPin(1111);
        atm.authenticate();
        atm.withdrawCash(2650);
        atm.ejectCard();

        System.out.println();

        // ── Abort scenario: ₹2660 has ₹10 remainder — no denomination covers it
        // Expect: transaction aborted, inventory unchanged, session continues cleanly
        atm.insertCard(account);
        atm.insertPin(1111);
        atm.authenticate();
        try {
            atm.withdrawCash(2660);          // ← should throw before touching inventory
        } catch (Exception e) {
            System.err.println("Transaction aborted: " + e.getMessage());
        }
        atm.ejectCard();                     // ← still works; session is unaffected

        System.out.println();

        // ── Out-of-order call guard ───────────────────────────────────────────
        try {
            atm.withdrawCash(10);
        } catch (Exception e) {
            System.err.println("Expected error: " + e.getMessage());
        }
    }
}

