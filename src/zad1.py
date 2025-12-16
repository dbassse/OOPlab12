#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# ================================
#    МОДЕЛИ ДАННЫХ
# ================================

@dataclass(frozen=True)
class Owner:
    id: int
    name: str
    phone: str


@dataclass(frozen=True)
class Pet:
    id: int
    name: str
    species: str
    breed: str
    age: int
    owner_id: int


# ================================
#    РЕПОЗИТОРИЙ ДЛЯ РАБОТЫ С БД
# ================================

class PetRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._create_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_db(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS owners (
                owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT NOT NULL,
                owner_phone TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pets (
                pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_name TEXT NOT NULL,
                pet_species TEXT NOT NULL,
                pet_breed TEXT NOT NULL,
                pet_age INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES owners(owner_id)
                    ON DELETE CASCADE
            )
            """
        )

        conn.commit()
        conn.close()

    def add_owner(self, name: str, phone: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO owners (owner_name, owner_phone)
            VALUES (?, ?)
            """,
            (name, phone)
        )

        conn.commit()
        conn.close()

    def add_pet(self, name: str, species: str, breed: str, age: int, owner_id: int) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pets (pet_name, pet_species, pet_breed, pet_age, owner_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, species, breed, age, owner_id)
        )

        conn.commit()
        conn.close()

    def get_all_owners(self) -> list[Owner]:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT owner_id, owner_name, owner_phone
            FROM owners
            ORDER BY owner_name
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            Owner(id=row[0], name=row[1], phone=row[2])
            for row in rows
        ]

    def get_all_pets(self) -> list[Pet]:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.pet_id, p.pet_name, p.pet_species, p.pet_breed, p.pet_age, p.owner_id
            FROM pets p
            ORDER BY p.pet_name
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            Pet(id=row[0], name=row[1], species=row[2], breed=row[3], age=row[4], owner_id=row[5])
            for row in rows
        ]

    def get_pets_by_owner(self, owner_id: int) -> list[Pet]:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.pet_id, p.pet_name, p.pet_species, p.pet_breed, p.pet_age, p.owner_id
            FROM pets p
            WHERE p.owner_id = ?
            ORDER BY p.pet_name
            """,
            (owner_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            Pet(id=row[0], name=row[1], species=row[2], breed=row[3], age=row[4], owner_id=row[5])
            for row in rows
        ]

    def get_owner_by_id(self, owner_id: int) -> Owner | None:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT owner_id, owner_name, owner_phone
            FROM owners
            WHERE owner_id = ?
            """,
            (owner_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return Owner(id=row[0], name=row[1], phone=row[2])
        return None


# ===========================================================
#    ФУНКЦИИ ДЛЯ ФОРМАТИРОВАННОГО ВЫВОДА
# ===========================================================

def display_owners(owners: list[Owner]) -> None:
    if not owners:
        print("Список владельцев пуст.")
        return

    line = '+{}+{}+{}+'.format(
        '-' * 6,
        '-' * 25,
        '-' * 15
    )

    print(line)
    print('| {:^6} | {:^25} | {:^15} |'.format(
        "ID", "Имя владельца", "Телефон"
    ))
    print(line)

    for owner in owners:
        print('| {:^6} | {:^25} | {:^15} |'.format(
            owner.id, owner.name, owner.phone
        ))
    print(line)


def display_pets(pets: list[Pet], show_owner: bool = False) -> None:
    if not pets:
        print("Список животных пуст.")
        return

    if show_owner:
        line = '+{}+{}+{}+{}+{}+{}+'.format(
            '-' * 6,
            '-' * 15,
            '-' * 15,
            '-' * 20,
            '-' * 6,
            '-' * 15
        )

        print(line)
        print('| {:^6} | {:^15} | {:^15} | {:^20} | {:^6} | {:^15} |'.format(
            "ID", "Кличка", "Вид", "Порода", "Возраст", "ID владельца"
        ))
        print(line)

        for pet in pets:
            print('| {:^6} | {:^15} | {:^15} | {:^20} | {:^6} | {:^15} |'.format(
                pet.id, pet.name, pet.species, pet.breed, pet.age, pet.owner_id
            ))
    else:
        line = '+{}+{}+{}+{}+{}+'.format(
            '-' * 6,
            '-' * 15,
            '-' * 15,
            '-' * 20,
            '-' * 6
        )

        print(line)
        print('| {:^6} | {:^15} | {:^15} | {:^20} | {:^6} |'.format(
            "ID", "Кличка", "Вид", "Порода", "Возраст"
        ))
        print(line)

        for pet in pets:
            print('| {:^6} | {:^15} | {:^15} | {:^20} | {:^6} |'.format(
                pet.id, pet.name, pet.species, pet.breed, pet.age
            ))
    print(line)


# ================================================
#    CLI (КОМАНДНАЯ СТРОКА)
# ================================================

def main(command_line=None):
    # Парсер пути к базе
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        required=False,
        default=str(Path.home() / "pets.db"),
        help="Путь к файлу базы данных"
    )

    # Основной парсер
    parser = argparse.ArgumentParser(
        "pets",
        description="Система учета домашних животных"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Добавление владельца
    add_owner = subparsers.add_parser(
        "add_owner",
        parents=[file_parser],
        help="Добавить владельца животного"
    )
    add_owner.add_argument("-n", "--name", required=True, help="Имя владельца")
    add_owner.add_argument("-p", "--phone", required=True, help="Телефон владельца")

    # Добавление животного
    add_pet = subparsers.add_parser(
        "add_pet",
        parents=[file_parser],
        help="Добавить животное"
    )
    add_pet.add_argument("-n", "--name", required=True, help="Кличка животного")
    add_pet.add_argument("-s", "--species", required=True, help="Вид животного")
    add_pet.add_argument("-b", "--breed", required=True, help="Порода животного")
    add_pet.add_argument("-a", "--age", required=True, type=int, help="Возраст животного")
    add_pet.add_argument("-o", "--owner", required=True, type=int, help="ID владельца")

    # Показать всех владельцев
    subparsers.add_parser(
        "display_owners",
        parents=[file_parser],
        help="Показать всех владельцев"
    )

    # Показать всех животных
    subparsers.add_parser(
        "display_pets",
        parents=[file_parser],
        help="Показать всех животных"
    )

    # Выборка животных по владельцу
    select_pets = subparsers.add_parser(
        "select_pets_by_owner",
        parents=[file_parser],
        help="Показать животных по владельцу"
    )
    select_pets.add_argument("-o", "--owner", required=True, type=int, help="ID владельца")

    # Разбор аргументов
    args = parser.parse_args(command_line)

    # Работа с БД
    repo = PetRepository(Path(args.db))

    if args.command == "add_owner":
        try:
            repo.add_owner(args.name, args.phone)
            print(f"Владелец '{args.name}' успешно добавлен!")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении владельца: {e}")

    elif args.command == "add_pet":
        try:
            # Проверяем существование владельца
            owner = repo.get_owner_by_id(args.owner)
            if not owner:
                print(f"Ошибка: Владелец с ID {args.owner} не найден!")
                return

            repo.add_pet(args.name, args.species, args.breed, args.age, args.owner)
            print(f"Животное '{args.name}' успешно добавлено!")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении животного: {e}")

    elif args.command == "display_owners":
        try:
            owners = repo.get_all_owners()
            display_owners(owners)
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка владельцев: {e}")

    elif args.command == "display_pets":
        try:
            pets = repo.get_all_pets()
            display_pets(pets, show_owner=True)
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка животных: {e}")

    elif args.command == "select_pets_by_owner":
        try:
            # Проверяем существование владельца
            owner = repo.get_owner_by_id(args.owner)
            if not owner:
                print(f"Ошибка: Владелец с ID {args.owner} не найден!")
                return

            pets = repo.get_pets_by_owner(args.owner)
            print(f"Животные владельца '{owner.name}' (ID: {owner.id}):")
            display_pets(pets, show_owner=False)
        except sqlite3.Error as e:
            print(f"Ошибка при выборке животных: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()