package design_patterns.singleton_design_pattern;

import design_patterns.singleton_design_pattern.singleton.BillPughSingleton;
import design_patterns.singleton_design_pattern.singleton.DCLSingleton;
import design_patterns.singleton_design_pattern.singleton.EagerSingleton;
import design_patterns.singleton_design_pattern.singleton.EnumSingleton;
import design_patterns.singleton_design_pattern.singleton.LazySingleton;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.reflect.Constructor;

/**
 * Demo runner for Singleton design patterns.
 * Demonstrates basic instantiation and illustrates reflection & serialization attacks.
 */
public class SingletonDemo {
    public static void main(String[] args) {
        System.out.println("=== Singleton Design Pattern Demo ===");

        // 1. Eager Initialization
        System.out.println("\n--- 1. Eager Initialization ---");
        EagerSingleton eager1 = EagerSingleton.getInstance();
        EagerSingleton eager2 = EagerSingleton.getInstance();
        System.out.println("eager1 hashcode: " + eager1.hashCode());
        System.out.println("eager2 hashcode: " + eager2.hashCode());
        System.out.println("eager1 == eager2: " + (eager1 == eager2));

        // 2. Lazy Initialization
        System.out.println("\n--- 2. Lazy Initialization ---");
        LazySingleton lazy1 = LazySingleton.getInstance();
        LazySingleton lazy2 = LazySingleton.getInstance();
        System.out.println("lazy1 hashcode: " + lazy1.hashCode());
        System.out.println("lazy2 hashcode: " + lazy2.hashCode());
        System.out.println("lazy1 == lazy2: " + (lazy1 == lazy2));

        // 3. Double-Checked Locking (DCL)
        System.out.println("\n--- 3. Double-Checked Locking ---");
        DCLSingleton dcl1 = DCLSingleton.getInstance();
        DCLSingleton dcl2 = DCLSingleton.getInstance();
        System.out.println("dcl1 hashcode: " + dcl1.hashCode());
        System.out.println("dcl2 hashcode: " + dcl2.hashCode());
        System.out.println("dcl1 == dcl2: " + (dcl1 == dcl2));

        // 4. Enum Singleton
        System.out.println("\n--- 4. Enum Singleton ---");
        EnumSingleton enum1 = EnumSingleton.INSTANCE;
        EnumSingleton enum2 = EnumSingleton.INSTANCE;
        enum1.setValue("Testing Enum");
        System.out.println("enum1 hashcode: " + enum1.hashCode());
        System.out.println("enum2 hashcode: " + enum2.hashCode());
        System.out.println("enum1 == enum2: " + (enum1 == enum2));
        enum2.doSomething();

        // 5. Bill Pugh Singleton
        System.out.println("\n--- 5. Bill Pugh Singleton ---");
        BillPughSingleton bp1 = BillPughSingleton.getInstance();
        BillPughSingleton bp2 = BillPughSingleton.getInstance();
        System.out.println("bp1 hashcode: " + bp1.hashCode());
        System.out.println("bp2 hashcode: " + bp2.hashCode());
        System.out.println("bp1 == bp2: " + (bp1 == bp2));

        // --- ATTACK DEMONSTRATIONS ---
        System.out.println("\n=== SECURITY ATTACK DEMONSTRATIONS ===");

        // Reflection Attack
        System.out.println("\n--- A. Reflection Attack ---");
        try {
            // Attacking EagerSingleton
            Constructor<EagerSingleton> constructor = EagerSingleton.class.getDeclaredConstructor();
            constructor.setAccessible(true);
            EagerSingleton eagerReflected = constructor.newInstance();

            System.out.println("Eager original instance hashcode: " + eager1.hashCode());
            System.out.println("Eager reflected instance hashcode: " + eagerReflected.hashCode());
            System.out.println("Is Eager Singleton broken by reflection? " + (eager1 != eagerReflected));
        } catch (Exception e) {
            System.out.println("Error reflectively accessing EagerSingleton: " + e.getMessage());
        }

        try {
            System.out.println("\nAttempting Reflection Attack on EnumSingleton...");
            // Attacking EnumSingleton
            // Enum constructors take (String name, int ordinal) parameters internally
            Constructor<EnumSingleton> enumConstructor = EnumSingleton.class.getDeclaredConstructor(String.class, int.class);
            enumConstructor.setAccessible(true);
            EnumSingleton enumReflected = enumConstructor.newInstance("REFLECTION_INSTANCE", 1);
            System.out.println("Enum reflected instance created: " + enumReflected);
        } catch (Exception e) {
            // Expected: IllegalArgumentException: Cannot reflectively create enum objects
            System.out.println("Result: Enum Singleton protected! Exception caught: " + e.toString());
        }

        // Serialization Attack
        System.out.println("\n--- B. Serialization Attack ---");
        try {
            // Attacking EagerSingleton
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(eager1);
            oos.close();

            ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bais);
            EagerSingleton eagerDeserialized = (EagerSingleton) ois.readObject();
            ois.close();

            System.out.println("Eager original instance hashcode: " + eager1.hashCode());
            System.out.println("Eager deserialized instance hashcode: " + eagerDeserialized.hashCode());
            System.out.println("Is Eager Singleton broken by serialization? " + (eager1 != eagerDeserialized));
        } catch (Exception e) {
            System.out.println("Error during EagerSingleton serialization: " + e.getMessage());
        }

        try {
            // Attacking EnumSingleton
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(enum1);
            oos.close();

            ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bais);
            EnumSingleton enumDeserialized = (EnumSingleton) ois.readObject();
            ois.close();

            System.out.println("\nEnum original instance hashcode: " + enum1.hashCode());
            System.out.println("Enum deserialized instance hashcode: " + enumDeserialized.hashCode());
            System.out.println("Is Enum Singleton broken by serialization? " + (enum1 != enumDeserialized));
            System.out.println("Does Enum deserialized maintain the same value? " + enumDeserialized.getValue());
        } catch (Exception e) {
            System.out.println("Error during EnumSingleton serialization: " + e.getMessage());
        }
    }
}
