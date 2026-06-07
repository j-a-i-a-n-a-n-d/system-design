package design_patterns.state_design_patern.state;

/**
 * State interface: declares the three actions a vending-machine state must handle.
 * Each concrete state decides what happens and which state comes next.
 *
 * Diagram: State { insertCoin() / ejectCoin() / dispense() }
 */
public interface State {
    void insertCoin(Context context);
    void ejectCoin(Context context);
    void dispense(Context context);
}
