package design_patterns.mediator_design_pattern.component;

import design_patterns.mediator_design_pattern.mediator.ChatMediator;

public class User {
    private final String name;
    private final ChatMediator mediator;

    public User(String name, ChatMediator mediator) {
        this.name = name;
        this.mediator = mediator;
        mediator.addUser(this);
    }

    public void send(String message) {
        System.out.println("[" + name + "] sends: " + message);
        mediator.sendMessage(message, this); // only talks to mediator
    }

    public void receive(String message) {
        System.out.println("[" + name + "] receives: " + message);
    }

    public String getName() {
        return name;
    }
}
