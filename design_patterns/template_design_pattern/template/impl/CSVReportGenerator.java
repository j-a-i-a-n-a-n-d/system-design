package template.impl;

import template.DataReportGenerator;

public class CSVReportGenerator extends DataReportGenerator {

    @Override
    protected String reportType() {
        return "CSV Sales Report";
    }

    @Override
    protected void fetchData() {
        System.out.println("[Step 1] Fetching raw sales data from the database...");
        System.out.println("         → Loaded 1,200 rows from sales_transactions table.");
    }

    @Override
    protected void processData() {
        System.out.println("[Step 2] Processing: filtering nulls, grouping by region...");
        System.out.println("         → Aggregated into 5 regional summaries.");
    }

    @Override
    protected void formatReport() {
        System.out.println("[Step 3] Formatting data as CSV...");
        System.out.println("         region,total_sales,units_sold");
        System.out.println("         North,42500.00,850");
        System.out.println("         South,38200.00,764");
        System.out.println("         East,51000.00,1020");
        System.out.println("         West,29800.00,596");
        System.out.println("         Central,33100.00,662");
    }

    @Override
    protected void exportReport() {
        System.out.println("[Step 4] Exporting CSV to /reports/sales_report.csv ✓");
    }
}
