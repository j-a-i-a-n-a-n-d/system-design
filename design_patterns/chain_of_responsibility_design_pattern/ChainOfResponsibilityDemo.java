package design_patterns.chain_of_responsibility_design_pattern;

import design_patterns.chain_of_responsibility_design_pattern.cor.HttpRequest;
import design_patterns.chain_of_responsibility_design_pattern.cor.handler.ApiHandler;
import design_patterns.chain_of_responsibility_design_pattern.cor.handler.AuthHandler;
import design_patterns.chain_of_responsibility_design_pattern.cor.handler.RoleHandler;

public class ChainOfResponsibilityDemo {
    public static void main() {

        AuthHandler auth = new AuthHandler();
        RoleHandler role = new RoleHandler("ADMIN");
        ApiHandler api = new ApiHandler();

        auth.setNext(role);
        role.setNext(api);

        System.out.println("--- Request 1: no token ---");
        auth.handle(new HttpRequest("u1", "", "ADMIN", "/in"));

        System.out.println("\n--- Request 2: wrong role ---");
        auth.handle(new HttpRequest("u1", "tok123", "GUEST", "/in"));

        System.out.println("\n--- Request 3: valid ---");
        auth.handle(new HttpRequest("u1", "tok123", "ADMIN", "/in"));

    }
}