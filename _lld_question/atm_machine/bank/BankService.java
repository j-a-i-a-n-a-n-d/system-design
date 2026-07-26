package _lld_question.atm_machine.bank;

import _lld_question.atm_machine.user.Account;

public interface BankService {
    Account getAccount(Account cardNo);

    boolean authenticate(Account account);

    double getBalance(Account account);

    double debitMoney(Account account, int amount) throws Exception;
}
