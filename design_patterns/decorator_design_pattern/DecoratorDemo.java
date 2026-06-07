import concrete.Coffee;
import concrete.impl.SimpleCoffee;
import concrete.impl.LatteCoffee;
import decorator.impl.MilkDecorator;
import decorator.impl.SugarDecorator;

public class DecoratorDemo {
    public static void main(String[] args) {
        // Base coffee
        Coffee coffee = new SimpleCoffee();
        System.out.println(coffee.getDescription() + " $" + coffee.getCost());
        coffee = new MilkDecorator(coffee);
        System.out.println(coffee.getDescription() + " $" + coffee.getCost());
        coffee = new SugarDecorator(coffee);
        System.out.println(coffee.getDescription() + " $" + coffee.getCost());

        // Latte coffee
        Coffee coffeeLatte = new LatteCoffee();
        System.out.println(coffeeLatte.getDescription() + " $" + coffeeLatte.getCost());
        coffeeLatte = new MilkDecorator(coffeeLatte);
        System.out.println(coffeeLatte.getDescription() + " $" + coffeeLatte.getCost());
        coffeeLatte = new SugarDecorator(coffeeLatte);
        System.out.println(coffeeLatte.getDescription() + " $" + coffeeLatte.getCost());

    }
}
