package design_patterns.state_design_patern.state;

/**
 * IdleState: the vending machine is idle — no coin has been inserted.
 *
 * Diagram:
 *   insertCoin  → transitions to HasCoinState
 *   dispense    → prints "insert coin first" (invalid action)
 *   ejectCoin   → nothing to eject
 */
public class IdleState implements State {

    @Override
    public void insertCoin(Context context) {
        System.out.println("[IdleState]     Coin inserted. Moving to HasCoinState.");
        context.setState(new HasCoinState());
    }

    @Override
    public void ejectCoin(Context context) {
        System.out.println("[IdleState]     No coin to eject.");
    }

    @Override
    public void dispense(Context context) {
        System.out.println("[IdleState]     Please insert a coin first.");
    }
}
