
import systems.Lights;
import systems.SoundSystem;
import systems.TV;

public class HomeTheaterFacade {
    private TV tv;
    private SoundSystem sound;
    private Lights lights;

    public HomeTheaterFacade(TV tv, SoundSystem sound, Lights lights) {
        this.tv = tv;
        this.sound = sound;
        this.lights = lights;
    }

    public void watchMovie() {
        System.out.println("Setting up Home Theater...");
        lights.dim(20);
        tv.on();
        sound.on();
        sound.setVolume(50);
        System.out.println("Movie is starting!");
    }

    public void setVolume(int level) {
        System.out.println("Adjusting volume through Facade...");
        sound.setVolume(level);
    }

    public void endMovie() {
        System.out.println("Shutting down Home Theater...");
        tv.off();
        sound.off();
        lights.on();
        System.out.println("System OFF.");
    }
}
