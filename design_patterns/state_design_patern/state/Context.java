package design_patterns.state_design_patern.state;

/**
 * Context (VendingMachine): holds the currentState and delegates each user
 * action to it.  Implements the three operations declared by the State interface.
 *
 * Diagram: Context { currentState: State | setState() / request() }
 */
public class Context {

    private State currentState;

    /** Start in IdleState — no coin inserted yet. */
    public Context() {
        this.currentState = new IdleState();
    }

    public void setState(State state) {
        this.currentState = state;
    }

    public State getState() {
        return currentState;
    }

    // --- Delegating request methods ---

    public void insertCoin() {
        currentState.insertCoin(this);
    }

    public void ejectCoin() {
        currentState.ejectCoin(this);
    }

    public void dispense() {
        currentState.dispense(this);
    }
}
