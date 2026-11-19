import csv
from pathlib import Path

from school import School, load_school


def export_payroll(school: School, path: Path) -> None:
    fields = ("ПІБ", "Посада", "Базова ставка", "Розрахована зарплата")
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        print(f"{fields[0]:<29} {fields[1]:<10} {fields[2]:>14} {fields[3]:>22}")
        print("-" * 78)
        for employee in school.employees:
            salary = employee.salary()
            writer.writerow((employee.full_name, employee.role,
                             f"{employee.base_salary:.2f}", f"{salary:.2f}"))
            print(f"{employee.full_name:<29} {employee.role:<10}"
                  f" {employee.base_salary:>14.2f} {salary:>22.2f}")


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    school = load_school(folder)
    export_payroll(school, folder / "salaries.csv")
    print("\nТаблицю збережено у salaries.csv")
