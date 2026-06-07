package design_patterns.chain_of_responsibility_design_pattern.cor.handler;

import design_patterns.chain_of_responsibility_design_pattern.cor.BaseHandler;
import design_patterns.chain_of_responsibility_design_pattern.cor.HttpRequest;

public class RoleHandler extends BaseHandler {
    private final String requiredRole;

    public RoleHandler(String requiredRole) {
        this.requiredRole = requiredRole;
    }

    @Override
    public void handle(HttpRequest request) {
        System.out.println("[Role] Checking role...");
        if (!request.getUserRole().equals(requiredRole)) {
            System.out.println("[Role] BLOCKED — need "
                    + requiredRole + ", got " + request.getUserRole());
            return;
        }
        System.out.println("[Role] Role OK. Passing on.");
        passToNext(request);
    }
}
