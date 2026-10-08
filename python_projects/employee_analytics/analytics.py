from data import employees

def list_employees():
    for emp in employees.values():
        print(emp)

def find_employee(emp_id):
    return employees.get(emp_id, None)

def filter_by_department(department):
    return [emp for emp in employees.values() if emp.department == department]

def calculate_average_salary():
    total_salary = sum(emp.salary for emp in employees.values())
    return total_salary / len(employees) if employees else 0

def find_highest_salary():
    return max(emp.salary for emp in employees.values())

def find_lowest_salary():
    return min(emp.salary for emp in employees.values())

def group_by_department():
    grouped = {}
    for emp in employees.values():
        dept = emp.department
        if dept not in grouped:
            grouped[dept] = {"names": [], "total_salary": 0}
        grouped[dept]["names"].append(emp.name)
        grouped[dept]["total_salary"] += emp.salary
    return grouped

def calculate_department_averages():
    grouped = group_by_department()
    department_averages = {}
    for dept, info in grouped.items():
        total_salary = info["total_salary"]
        count = len(info["names"])
        department_averages[dept] = total_salary / count if count else 0
    return department_averages


# def group_by_department():
#     grouped = {}
#     for emp in employees.values():   # or just employees if it's a list
#         dept = emp.department
#         if dept not in grouped:
#             grouped[dept] = {"names": [], "total_salary": 0}

#         # add employee name
#         grouped[dept]["names"].append(emp.name)

#         # increment salary total
#         grouped[dept]["total_salary"] += emp.salary

#     return grouped


# def calculate_department_averages():
# # using above function group_by_department to get the employees grouped by department
#     grouped = group_by_department()
#     department_averages = {}
#     for dept, employees in grouped.items():
#         total_salary = sum(emp.salary for emp in employees)
#         department_averages[dept] = total_salary / len(employees)
#     return department_averages



#     # department_salaries = {}
#     # for emp in employees.values():
#     #     dept = emp.department
#     #     if dept not in department_salaries:
#     #         department_salaries[dept] = []
#     #     department_salaries[dept].append(emp.salary)

#     # department_averages = {dept: sum(salaries) / len(salaries) for dept, salaries in department_salaries.items()}
#     # return department_averages