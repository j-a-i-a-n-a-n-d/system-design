package design_patterns.composite_design_pattern;

import java.util.ArrayList;
import java.util.List;

public class Manager implements Employee {
    private String name;
    private String department;
    private List<Employee> subordinates = new ArrayList<>();

    public Manager(String name, String department) {
        this.name = name;
        this.department = department;
    }

    public void addEmployee(Employee employee) {
        subordinates.add(employee);
    }

    public void removeEmployee(Employee employee) {
        subordinates.remove(employee);
    }

    @Override
    public void showDetails() {
        System.out.println("\nManager: " + name + " | Department: " + department);
        System.out.println("Subordinates of " + name + ":");
        for (Employee employee : subordinates) {
            employee.showDetails();
        }
    }
}
