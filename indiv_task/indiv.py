#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу с людьми и днями рождения
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS people (
        person_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_name TEXT NOT NULL,
        person_birth TEXT NOT NULL,
        FOREIGN KEY(person_id) REFERENCES pnumbers(person_id)
        )
        """
    )

    # Создать таблицу с номерами телефонов людей
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS pnumbers (
        person_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pnumber INTEGER NOT NULL
        )
        """
    )
    conn.close()


def add_people(
    database_path: Path, name: str, pnumber: int, birth: str
) -> None:
    """
    Добавить человека в БД
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT person_id FROM people WHERE person_name = ?
        """,
        (name,),
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO people (person_name, person_birth) VALUES (?, ?)
            """,
            (name, birth),
        )
        person_id = cursor.lastrowid

    else:
        person_id = row[0]
        # Добавить информацию о человеке
    cursor.execute(
        """
        INSERT INTO pnumbers (person_id,  pnumber)
        VALUES (?, ?)
        """,
        (person_id, pnumber),
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Вывести всех людей из БД
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.person_name, people.person_birth, pnumbers.pnumber
        FROM pnumbers
        INNER JOIN people ON people.person_id = pnumbers.person_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "pnumber": row[1],
            "birth": row[2],
        }
        for row in rows
    ]


def find_people(database_path: Path, birth: str) -> t.List[t.Dict[str, t.Any]]:
    """
    Вывод на экран информации о человека по дате рождения
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.person_name, people.person_birth, pnumbers.pnumber
        FROM pnumbers
        INNER JOIN people ON people.person_id = pnumbers.person_id
        WHERE people.person_birth LIKE ? || '%'
        """,
        (birth,),
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) == 0:
        return []

    return [
        {
            "name": row[0],
            "birth": row[1],
            "pnumber": row[2],
        }
        for row in rows
    ]


def display_people(people_list: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Вывести людей из списка
    """
    if people_list:
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 14, "-" * 19
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^14} | {:^19} |".format(
                "№п/п", "Фамилия Имя", "Дата рождения", "Номер телефона"
            )
        )
        print(line)

        for nmbr, person in enumerate(people_list, 1):
            print(
                "| {:>4} | {:<30} | {:<14} | {:>19} |".format(
                    nmbr,
                    person.get("name", ""),
                    person.get("pnumber", ""),
                    person.get("birth", ""),
                )
            )
        print(line)

    else:
        print("Список пуст.")


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.cwd() / "people_data.db"),
        help="Имя файла БД",
    )

    # Создать основной парсер командной строки
    parser = argparse.ArgumentParser("people")
    parser.add_argument(
        "--version", action="version", version="%(prog)s alpha beta 0.0.1"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления работника
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Добавить нового человека"
    )

    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="Имя и фамилия человека",
    )

    add.add_argument(
        "-p", "--pnumber", type=int, action="store", help="Номер телефона"
    )

    add.add_argument(
        "-b", "--birth", action="store", required=True, help="Дата рождения"
    )

    # Создать субпарсер для отображения всех людей
    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Отобразить всех людей"
    )

    # Создать субпарсер для поиска людей по фамилии
    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Выбор человека"
    )

    select.add_argument(
        "-b", "--birth", action="store", required=True, help="Дата рождения"
    )

    # Выполнить разбор аргументов командной строки
    args = parser.parse_args(command_line)

    # Получить путь к файлу БД
    db_path = Path(args.db)
    create_db(db_path)

    match args.command:
        # Добавить человека
        case "add":
            add_people(db_path, args.name, args.pnumber, args.birth)
        # Отобразить всех людей
        case "display":
            display_people(select_all(db_path))
        # Выбрать людей по дате рождения
        case "select":
            display_people(find_people(db_path, args.birth))


if __name__ == "__main__":
    main()
