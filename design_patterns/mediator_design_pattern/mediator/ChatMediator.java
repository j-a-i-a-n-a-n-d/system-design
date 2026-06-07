package design_patterns.mediator_design_pattern.mediator;

import design_patterns.mediator_design_pattern.component.User;

public interface ChatMediator {
    void sendMessage(String message, User sender);

    void addUser(User user);
}
