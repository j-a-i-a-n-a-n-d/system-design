package design_patterns.state_design_patern;

import design_patterns.state_design_patern.state.Context;

/**
 * StateDemo: entry point demonstrating the Vending Machine State pattern.
 *
 * Cycle from diagram:
 * IdleState --insertCoin--> HasCoinState --dispense--> DispensingState
 * --dispense--> IdleState
 * HasCoinState --ejectCoin--> IdleState
 */
public class StateDemo {
    public static void main(String[] args) {

        Context machine = new Context(); // starts in IdleState

        System.out.println("=== Scenario 1: Normal buy cycle ===");
        machine.insertCoin(); // Idle → HasCoin
        machine.dispense(); // HasCoin → Dispensing
        // machine.dispense(); // Dispensing → releases item, back to Idle

        System.out.println("\n=== Scenario 2: Insert then eject ===");
        machine.insertCoin(); // Idle → HasCoin
        machine.ejectCoin(); // HasCoin → Idle

        System.out.println("\n=== Scenario 3: Invalid action — dispense without coin ===");
        machine.dispense(); // Idle → "Please insert a coin first"
    }
}
