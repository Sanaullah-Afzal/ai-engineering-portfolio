from dataclasses import dataclass, field
from typing import List

@dataclass
# Automatically generates __init__, __repr__, and comparison methods
class Employee:
    id: int
    name: str
    department: str
    salary: float

@dataclass
class Department:
    name: str
    employees: List[Employee] = field(default_factory=list)
    # field(default_factory=list) ensures each department gets its own list (not shared across instances)

    def add_employee(self, employee: Employee) -> None:
        self.employees.append(employee)

    def remove_employee(self, employee: Employee) -> None:
        self.employees.remove(employee)