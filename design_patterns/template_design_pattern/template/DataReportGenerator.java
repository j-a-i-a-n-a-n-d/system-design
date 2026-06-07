package template;

public abstract class DataReportGenerator {

    public final void generateReport() {
        fetchData();
        processData();
        formatReport();
        exportReport();
    }

    protected abstract void fetchData();

    protected abstract void processData();

    protected abstract void formatReport();

    protected abstract void exportReport();

    protected String reportType() {
        return this.getClass().getSimpleName();
    }
}
