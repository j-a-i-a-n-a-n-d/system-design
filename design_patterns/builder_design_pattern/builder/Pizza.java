package design_patterns.builder_design_pattern.builder;

public class Pizza {
    private String id;
    private String size;
    private String crustType;
    private boolean extraCheese;
    private Integer noOfMushrooms;
    private Integer noOfPepperoni;
    private Integer noOfOlives;
    private Integer cost;

    Pizza(PizzaBuilder pizzaBuilder) {
        this.id = pizzaBuilder.id;
        this.size = pizzaBuilder.size;
        this.crustType = pizzaBuilder.crustType;
        this.extraCheese = pizzaBuilder.extraCheese;
        this.noOfMushrooms = pizzaBuilder.noOfMushrooms;
        this.noOfPepperoni = pizzaBuilder.noOfPepperoni;
        this.noOfOlives = pizzaBuilder.noOfOlives;
        this.cost = pizzaBuilder.cost;
    }

    @Override
    public String toString() {
        return "Pizza [id=" + id + ", size=" + size + ", crustType=" + crustType + ", extraCheese="
                + extraCheese + ", noOfMushrooms=" + noOfMushrooms + ", noOfPepperoni=" + noOfPepperoni
                + ", noOfOlives=" + noOfOlives + ", cost=" + cost + "]";
    }

}
