import pytest
from models import Employee
from services import EmployeeRepository, ComplianceValidator
# from exceptions import InvalidSalaryError, EmployeeNotFoundError
import exceptions

def test_add_employee_invalid_salary():
    repo = EmployeeRepository()
    with pytest.raises(exceptions.InvalidSalaryError):
        repo.add_employee(Employee(1, "Test", "HR", 5000))

def test_find_employee_not_found():
    repo = EmployeeRepository()
    with pytest.raises(exceptions.EmployeeNotFoundError):
        repo.find_employee(99)
