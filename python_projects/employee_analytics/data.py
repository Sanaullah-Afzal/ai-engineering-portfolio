from dataclasses import dataclass
import random

@dataclass
class Employee:
    id: int
    name: str
    department: str
    salary: float

    def __str__(self):
        return f"Employee(id={self.id}, name='{self.name}', department='{self.department}', salary={self.salary})"

names = [
    "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry",
    "Ivy", "Jack", "Sara", "Ahmed", "Fatima", "Bilal", "Zara", "Usman",
    "Ayesha", "Hassan", "Maryam", "Omar"
]

departments = ["HR", "Finance", "Engineering", "Marketing", "Sales", "AI"]

# Generate 25 fake employees
employees = {
    i+1: Employee(
        id=i+1,
        name=names[i % len(names)],
        department=random.choice(departments),
        salary=random.randint(50_000, 150_000)
    )
    for i in range(25)
}
