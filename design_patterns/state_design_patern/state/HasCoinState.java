package design_patterns.state_design_patern.state;

/**
 * HasCoinState: a coin has been inserted and is waiting for dispense action.
 *
 * Diagram:
 *   ejectCoin → transitions back to IdleState
 *   dispense  → transitions to DispensingState
 *   insertCoin → coin already inserted warning
 */
public class HasCoinState implements State {

    @Override
    public void insertCoin(Context context) {
        System.out.println("[HasCoinState]  Coin already inserted.");
    }

    @Override
    public void ejectCoin(Context context) {
        System.out.println("[HasCoinState]  Coin ejected. Returning to IdleState.");
        context.setState(new IdleState());
    }

    @Override
    public void dispense(Context context) {
        System.out.println("[HasCoinState]  Dispensing item... Moving to DispensingState.");
        context.setState(new DispensingState());
    }
}
