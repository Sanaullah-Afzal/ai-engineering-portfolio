import models
import services
import analytics
from models import Employee

def main():
    employee_repository = services.EmployeeRepository()
    validator = services.ComplianceValidator()
    # add employees
    employee_repository.add_employee(Employee(1, "John Doe", "HR", 50000.0))
    employee_repository.add_employee(models.Employee(2, "Jane Smith", "IT", 60000.0))
    employee_repository.add_employee(models.Employee(3, "Bob Johnson", "HR", 55000.0))
    employee_repository.add_employee(models.Employee(4, "Alice Williams", "IT", 70000.0))

    sal_analytics = analytics.SalaryAnalytics(employee_repository.all_employees())

    print(f"Average salary: {sal_analytics.average_salary():.2f}")
    print(f"Highest salary: {sal_analytics.highest_salary().name}")
    print(f"Lowest salary: {sal_analytics.lowest_salary()}")
    print(f"Department averages: {sal_analytics.department_averages()}")

    validator.validate_salary_range(employee_repository.find_employee(1), 0, 100000)

# guard ensures that the main() function only runs when the file is executed directly, not when imported.
if __name__ == "__main__":
    main()