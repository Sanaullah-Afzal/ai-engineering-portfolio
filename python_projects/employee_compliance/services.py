# Repository + Validator layer
from typing import Dict
from models import Employee
from exceptions import EmployeeNotFoundError, InvalidSalaryError, ComplianceViolationError

class EmployeeRepository:
    def __init__(self):
        self._employees: Dict[int, Employee] = {}

    def add_employee(self, employee: Employee) -> None:
        if employee.salary < 0:
            raise InvalidSalaryError("Salary cannot be negative")
        self._employees[employee.id] = employee

    def find_employee(self, emp_id: int) -> Employee:
        if emp_id not in self._employees:
            raise EmployeeNotFoundError(f"Employee {emp_id} not found")
        return self._employees[emp_id]

    def all_employees(self) -> Dict[int, Employee]:
        return self._employees

class ComplianceValidator:
    def validate_salary_range(self, employee: Employee, min_salary: float, max_salary: float) -> None:
        if not (min_salary <= employee.salary <= max_salary):
            raise ComplianceViolationError(
                f"Employee {employee.id} salary {employee.salary} out of range"
            )