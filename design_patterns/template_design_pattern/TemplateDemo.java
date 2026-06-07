import template.DataReportGenerator;
import template.impl.CSVReportGenerator;
import template.impl.HTMLReportGenerator;

public class TemplateDemo {
    public static void main() {

        DataReportGenerator csvReport = new CSVReportGenerator();
        DataReportGenerator htmlReport = new HTMLReportGenerator();

        csvReport.generateReport();
        htmlReport.generateReport();
    }
}
