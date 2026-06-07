package design_patterns.proxy_design_pattern;

import design_patterns.proxy_design_pattern.proxy.Image;
import design_patterns.proxy_design_pattern.proxy.ProxyImage;

public class ProxyDemo {
    public static void main(String[] args) {
        Image image = new ProxyImage("test_image.jpg");
        image.display();
        Image image2 = new ProxyImage("test_image2.jpg");
        image2.display();
    }
}
