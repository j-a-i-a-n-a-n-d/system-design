package _lld_question.atm_machine.bank.impl;

import _lld_question.atm_machine.bank.BankService;
import _lld_question.atm_machine.user.Account;

public class AXISBankService implements BankService {
    @Override
    public Account getAccount(Account account) {
        // Fetch More account Information From the Database
        return account;
    }

    @Override
    public boolean authenticate(Account account) {
        // Check with DB if the pin is same as that which is entered,
        return account.getPin() == 1111;
    }

    @Override
    public double getBalance(Account account) {
        // In reality implemented from DB
        return account.getBalance();
    }

    @Override
    public double debitMoney(Account account, int amount) {
        // Check from DB if there is enough money and update it
        if (!account.debitMoney(amount)) {
            try {
                throw new Exception("Insufficient Balance Sorry");
            } catch (Exception e) {
                System.err.println(e.getMessage());
            }
        }
        return amount;
    }
}
