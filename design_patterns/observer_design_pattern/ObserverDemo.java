
import observer.impl.MobileApp;
import observer.impl.WebDashboard;
import observer.SecureStock;

public class ObserverDemo {
    public static void main() {
        SecureStock appleStock = new SecureStock("Apple", 150.0);

        MobileApp mobileApp = new MobileApp();
        WebDashboard dashboard = new WebDashboard();

        appleStock.registerObserver(mobileApp);
        appleStock.registerObserver(dashboard);

        appleStock.setPrice(155.0);

        appleStock.removeObserver(mobileApp);
        appleStock.setPrice(160.0);
    }
}
