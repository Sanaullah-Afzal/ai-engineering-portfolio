from typing import Dict
from models import Employee, Department

class SalaryAnalytics:
    def __init__(self, employees: Dict[int, Employee]):
        self.employees = employees

    def average_salary(self) -> float: #how self works here
        return sum(emp.salary for emp in self.employees.values()) / len(self.employees)

    def highest_salary(self) -> Employee:
        highest = None
        for emp in self.employees.values():
            if highest is None or emp.salary > highest.salary:
                highest = emp
        return highest    

    def lowest_salary(self) -> Employee:
        # return min(self.employees.values(), key=lambda e: e.salary)
        return sorted(self.employees.values(), key=lambda e: e.salary, reverse=False)[0]
    
    def department_averages(self) -> Dict[str, float]:
        dept_salaries: Dict[str, list] = {}

        # Step 1: group salaries by department
        for emp in self.employees.values():
            if emp.department not in dept_salaries:
                dept_salaries[emp.department] = []
            dept_salaries[emp.department].append(emp.salary)

        # Step 2: calculate averages
        department_averages: Dict[str, float] = {}
        for dept, salaries in dept_salaries.items():
            total = sum(salaries)
            count = len(salaries)
            average = total / count if count else 0
            department_averages[dept] = average

        return department_averages
