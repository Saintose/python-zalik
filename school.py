import csv
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean


@dataclass(frozen=True)
class Student:
    surname: str
    first_name: str
    patronymic: str
    birth_year: int
    gender: str
    average_grade: float


@dataclass
class SchoolClass:
    grade: int
    letter: str
    students: list[Student] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"{self.grade}{self.letter}"

    def advance(self) -> bool:
        # Одинадцятий клас випускається, тому номер не змінюємо.
        if self.grade == 11:
            return False
        self.grade += 1
        return True


@dataclass
class Employee(ABC):
    full_name: str
    base_salary: float

    @property
    def role(self) -> str:
        return "Працівник"

    @abstractmethod
    def salary(self) -> float:
        raise NotImplementedError


@dataclass
class Teacher(Employee):
    teaching_years: int

    @property
    def role(self) -> str:
        return "Вчитель"

    def salary(self) -> float:
        return self.base_salary * self.teaching_years / 30


@dataclass
class Director(Teacher):
    management_years: int

    @property
    def role(self) -> str:
        return "Директор"

    def salary(self) -> float:
        return self.base_salary * self.teaching_years / 50 + self.management_years * 500


@dataclass
class Guard(Employee):
    total_years: int

    @property
    def role(self) -> str:
        return "Охоронець"

    def salary(self) -> float:
        return self.base_salary + self.total_years * 250


@dataclass
class School:
    classes: list[SchoolClass]
    employees: list[Employee]
    name: str = "Ліцей «Інтелект» Дарницького району м. Києва"
    address: str = "м. Київ, проспект Миколи Бажана, 34-А"

    def statistics(self) -> list[tuple[str, str]]:
        pupils = [student for group in self.classes for student in group.students]
        counts = Counter(student.gender for student in pupils)
        sizes = [len(group.students) for group in self.classes]
        total = len(pupils)
        boys = counts["Х"] * 100 / total if total else 0
        girls = counts["Д"] * 100 / total if total else 0

        def describe_size(size: int) -> str:
            # За однакової наповнюваності вказуємо всі такі класи.
            names = ", ".join(group.name for group in self.classes if len(group.students) == size)
            return f"{size} ({names})"

        return [
            ("Усього учнів", str(total)),
            ("Хлопці", f"{boys:.2f} %"),
            ("Дівчата", f"{girls:.2f} %"),
            ("Середня наповнюваність класу", f"{mean(sizes):.2f}" if sizes else "0.00"),
            ("Максимальна наповнюваність", describe_size(max(sizes)) if sizes else "—"),
            ("Мінімальна наповнюваність", describe_size(min(sizes)) if sizes else "—"),
        ]

    def promote_classes(self) -> None:
        self.classes = [group for group in self.classes if group.advance()]


def load_school(data_dir: Path) -> School:
    # Паралель і літера разом визначають клас, до якого належить учень.
    classes: dict[tuple[int, str], SchoolClass] = {}
    with (data_dir / "classes.csv").open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            grade = int(row["grade"])
            letter = row["letter"].strip()
            key = (grade, letter)
            if not 1 <= grade <= 11 or not letter or key in classes:
                raise ValueError(f"Некоректний або повторний клас {grade}{letter}")
            classes[key] = SchoolClass(grade, letter)

    with (data_dir / "students.csv").open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            key = (int(row["grade"]), row["letter"].strip())
            gender = row["gender"].strip()
            mark = float(row["average_grade"])
            if key not in classes or gender not in {"Х", "Д"} or not 1 <= mark <= 12:
                raise ValueError(f"Некоректний запис учня {row['surname']}")
            classes[key].students.append(Student(
                row["surname"], row["first_name"], row["patronymic"],
                int(row["birth_year"]), gender, mark,
            ))

    employees: list[Employee] = [
        Director("Коваленко Олена Іванівна", 15000, 20, 8),
        Teacher("Бондар Ірина Петрівна", 12000, 15),
        Teacher("Шевченко Максим Олегович", 12000, 10),
        Guard("Ткачук Сергій Андрійович", 11000, 12),
    ]
    ordered_classes = sorted(classes.values(), key=lambda group: (group.grade, group.letter))
    return School(ordered_classes, employees)
