import systems.Lights;
import systems.SoundSystem;
import systems.TV;

public class FacadeDemo {
    public static void main(String[] args) {
        // Complex subsystems
        TV tv = new TV();
        SoundSystem sound = new SoundSystem();
        Lights lights = new Lights();

        // Simple interface
        HomeTheaterFacade homeTheater = new HomeTheaterFacade(tv, sound, lights);

        // One command instead of manually managing all components
        homeTheater.watchMovie();

        System.out.println("\n--- Action Scene: Increasing Volume ---");
        homeTheater.setVolume(80);

        System.out.println("\n--- Dialogue Scene: Decreasing Volume ---");
        homeTheater.setVolume(30);

        System.out.println("\n--- Fast Forward 2 Hours ---\n");
        homeTheater.endMovie();
    }
}
