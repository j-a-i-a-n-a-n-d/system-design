package design_patterns.builder_design_pattern.builder;

public class PizzaBuilder {
    String id;
    String size;
    String crustType;
    boolean extraCheese;
    Integer noOfMushrooms;
    Integer noOfPepperoni;
    Integer noOfOlives;
    Integer cost;

    public PizzaBuilder setId(String id) {
        this.id = id;
        return this;
    }

    public PizzaBuilder setSize(String size) {
        this.size = size;
        return this;
    }

    public PizzaBuilder setCrustType(String crustType) {
        this.crustType = crustType;
        return this;
    }

    public PizzaBuilder setExtraCheese(boolean extraCheese) {
        this.extraCheese = extraCheese;
        return this;
    }

    public PizzaBuilder setNoOfMushrooms(int noOfMushrooms) {
        this.noOfMushrooms = noOfMushrooms;
        return this;
    }

    public PizzaBuilder setNoOfPepperoni(int noOfPepperoni) {
        this.noOfPepperoni = noOfPepperoni;
        return this;
    }

    public PizzaBuilder setNoOfOlives(int noOfOlives) {
        this.noOfOlives = noOfOlives;
        return this;
    }

    public PizzaBuilder setCost(int cost) {
        this.cost = cost;
        return this;
    }

    public Pizza build() {
        return new Pizza(this);
    }

}
