package design_patterns.mediator_design_pattern.mediator.impl;

import java.util.ArrayList;
import java.util.List;

import design_patterns.mediator_design_pattern.component.User;
import design_patterns.mediator_design_pattern.mediator.ChatMediator;

public class ChatRoom implements ChatMediator {
    private final List<User> users = new ArrayList<>();

    @Override
    public void addUser(User user) {
        users.add(user);
    }

    @Override
    public void sendMessage(String message, User sender) {
        users.forEach(u -> u.receive(sender.getName() + ": " + message));
    }
}