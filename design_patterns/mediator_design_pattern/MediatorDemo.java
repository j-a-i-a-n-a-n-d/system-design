package design_patterns.mediator_design_pattern;

import design_patterns.mediator_design_pattern.component.User;
import design_patterns.mediator_design_pattern.mediator.impl.ChatRoom;

public class MediatorDemo {
    public static void main(String[] args) {
        ChatRoom room = new ChatRoom();

        User alice = new User("Alice", room);
        User bob = new User("Bob", room);
        User carol = new User("Carol", room);

        alice.send("Hey everyone!");
        System.out.println();
        bob.send("Hi Alice & Carol!");
        System.out.println();
        carol.send("Hi Alice, Bob");
    }
}
