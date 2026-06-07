package design_patterns.chain_of_responsibility_design_pattern.cor;

public class HttpRequest {
    private final String userId;
    private final String token;
    private final String userRole;
    private final String path;

    public HttpRequest(String userId,
            String token,
            String userRole,
            String path) {
        this.userId = userId;
        this.token = token;
        this.userRole = userRole;
        this.path = path;
    }

    public String getUserId() {
        return userId;
    }

    public String getToken() {
        return token;
    }

    public String getUserRole() {
        return userRole;
    }

    public String getPath() {
        return path;
    }
}
