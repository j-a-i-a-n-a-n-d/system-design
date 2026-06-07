package design_patterns.chain_of_responsibility_design_pattern.cor;

public interface RequestHandler {
    void setNext(RequestHandler next);

    void handle(HttpRequest request);
}
