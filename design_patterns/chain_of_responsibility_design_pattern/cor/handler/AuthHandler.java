package design_patterns.chain_of_responsibility_design_pattern.cor.handler;

import design_patterns.chain_of_responsibility_design_pattern.cor.BaseHandler;
import design_patterns.chain_of_responsibility_design_pattern.cor.HttpRequest;

public class AuthHandler extends BaseHandler {
    @Override
    public void handle(HttpRequest request) {
        System.out.println("[Auth] Checking token...");
        if (request.getToken() == null || request.getToken().isEmpty()) {
            System.out.println("[Auth] BLOCKED — missing token.");
            return;
        }
        System.out.println("[Auth] Token valid. Passing on.");
        passToNext(request);
    }
}
