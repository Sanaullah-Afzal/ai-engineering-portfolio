from analytics import *

def main():
    while True:
        print("\nEmployee Analytics CLI")
        print("1. List employees")
        print("2. Find employee by ID")
        print("3. Filter by department")
        print("4. Average salary")
        print("5. Highest salary")
        print("6. Lowest salary")
        print("7. Group by department")
        print("8. Department averages")
        print("9. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            list_employees()
        elif choice == "2":
            emp_id = int(input("Enter employee ID: "))
            print(find_employee(emp_id))
        elif choice == "3":
            dept = input("Enter department: ")
            print(filter_by_department(dept))
        elif choice == "4":
            print(calculate_average_salary())
        elif choice == "5":
            print(find_highest_salary())
        elif choice == "6":
            print(find_lowest_salary())
        elif choice == "7":
            print(group_by_department())
        elif choice == "8":
            print(calculate_department_averages())
        elif choice == "9":
            break

if __name__ == "__main__":  #Only run this code if the file is being executed directly, not when it’s imported as a module
    main()   
