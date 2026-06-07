package template.impl;

import template.DataReportGenerator;

public class HTMLReportGenerator extends DataReportGenerator {

    @Override
    protected String reportType() {
        return "HTML Inventory Report";
    }

    @Override
    protected void fetchData() {
        System.out.println("[Step 1] Fetching inventory data from warehouse API...");
        System.out.println("         → Retrieved 320 SKUs across 4 warehouses.");
    }

    @Override
    protected void processData() {
        System.out.println("[Step 2] Processing: flagging low-stock items (qty < 10)...");
        System.out.println("         → 18 items flagged for reorder.");
    }

    @Override
    protected void formatReport() {
        System.out.println("[Step 3] Formatting data as HTML...");
        System.out.println("         <html><body>");
        System.out.println("           <h1>Inventory Report</h1>");
        System.out.println("           <table>");
        System.out.println("             <tr><th>SKU</th><th>Name</th><th>Qty</th><th>Status</th></tr>");
        System.out.println("             <tr><td>SKU-001</td><td>Widget A</td><td>8</td><td>⚠ Low</td></tr>");
        System.out.println("             <tr><td>SKU-042</td><td>Gadget B</td><td>145</td><td>✓ OK</td></tr>");
        System.out.println("           </table>");
        System.out.println("         </body></html>");
    }

    @Override
    protected void exportReport() {
        System.out.println("[Step 4] Emailing HTML report to warehouse-team@company.com ✓");
    }
}
