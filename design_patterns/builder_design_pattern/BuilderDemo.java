package design_patterns.builder_design_pattern;

import design_patterns.builder_design_pattern.builder.Pizza;
import design_patterns.builder_design_pattern.builder.PizzaBuilder;

public class BuilderDemo {
    public static void main(String[] args) {
        PizzaBuilder pizzaBuilder = new PizzaBuilder();
        pizzaBuilder.setId("1")
                .setSize("Large")
                .setCrustType("Thin")
                .setExtraCheese(true)
                .setNoOfMushrooms(2)
                .setNoOfPepperoni(3)
                .setNoOfOlives(4)
                .setCost(100);
        Pizza pizza = pizzaBuilder.build();
        System.out.println(pizza);

    }
}
