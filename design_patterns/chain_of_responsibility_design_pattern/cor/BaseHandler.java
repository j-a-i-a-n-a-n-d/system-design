package design_patterns.chain_of_responsibility_design_pattern.cor;

public abstract class BaseHandler implements RequestHandler {
    private RequestHandler next;

    @Override
    public void setNext(RequestHandler next) {
        this.next = next;
    }

    protected void passToNext(HttpRequest request) {
        if (next != null) {
            next.handle(request);
        } else {
            System.out.println("  [END] No more handlers.");
        }
    }
}
