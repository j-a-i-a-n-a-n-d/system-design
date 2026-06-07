package design_patterns.composite_design_pattern;

public class Designer implements Employee {
    private String name;
    private String position;
    private double salary;

    public Designer(String name, String position, double salary) {
        this.name = name;
        this.position = position;
        this.salary = salary;
    }

    @Override
    public void showDetails() {
        System.out.println("Designer: " + name + " | Position: " + position + " | Salary: $" + salary);
    }
}
