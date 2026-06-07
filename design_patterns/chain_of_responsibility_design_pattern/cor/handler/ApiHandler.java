package design_patterns.chain_of_responsibility_design_pattern.cor.handler;

import design_patterns.chain_of_responsibility_design_pattern.cor.BaseHandler;
import design_patterns.chain_of_responsibility_design_pattern.cor.HttpRequest;

public class ApiHandler extends BaseHandler {
    @Override
    public void handle(HttpRequest request) {
        // passToNext(request);
        System.out.println("[API] Processing: " + request.getPath());
        System.out.println("[API] Response: 200 OK");
    }
}
