package _lld_question.atm_machine.user;

public class Account {
    private String accountNumber;
    private String cardNo;
    private int balance;
    private int pin;

    public String getAccountNumber() {
        return accountNumber;
    }

    public void setAccountNumber(String accountNumber) {
        this.accountNumber = accountNumber;
    }

    public void setCardNo(String cardNo) {
        this.cardNo = cardNo;
    }

    public void setBalance(int balance) {
        this.balance = balance;
    }

    public void setPin(int pin) {
        this.pin = pin;
    }

    public String getCardNo() {
        return cardNo;
    }

    public int getBalance() {
        return balance;
    }

    public int getPin() {
        return pin;
    }

    public Account(String accountNumber, String cardNo, int balance, int pin) {
        this.accountNumber = accountNumber;
        this.cardNo = cardNo;
        this.balance = balance;
        this.pin = pin;
    }

    /**
     * Checks if there is enough balance to withdraw the amount.
     */
    public boolean debitMoney(int amount) {
        if (amount > balance)
            return false;
        balance -= amount;
        return true;
    }
}
