package design_patterns.state_design_patern.state;

/**
 * DispensingState: the item is being dispensed.
 *
 * Diagram:
 *   dispense   → release item, then transition back to IdleState
 *   insertCoin → invalid in this state
 *   ejectCoin  → cannot eject while dispensing
 */
public class DispensingState implements State {

    @Override
    public void insertCoin(Context context) {
        System.out.println("[DispensingState] Please wait — item is being dispensed.");
    }

    @Override
    public void ejectCoin(Context context) {
        System.out.println("[DispensingState] Cannot eject coin while dispensing.");
    }

    @Override
    public void dispense(Context context) {
        System.out.println("[DispensingState] Item released! Transitioning back to IdleState.");
        context.setState(new IdleState());
    }
}
