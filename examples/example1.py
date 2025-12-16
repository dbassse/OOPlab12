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
class Post:
    id: int
    title: str

@dataclass(frozen=True)
class Worker:
    name: str
    post: str
    year: int


# ================================
#    РЕПОЗИТОРИЙ ДЛЯ РАБОТЫ С БД
# ================================

class StaffRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._create_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_db(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_title TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workers (
                worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_name TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                worker_year INTEGER NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(post_id)
            )
            """
        )

        conn.commit()
        conn.close()

    def get_or_create_post(self, title: str) -> int:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT post_id FROM posts WHERE post_title = ?", (title,))
        row = cursor.fetchone()

        if row is None:
            cursor.execute("INSERT INTO posts (post_title) VALUES (?)", (title,))
            post_id = cursor.lastrowid
            conn.commit()
        else:
            post_id = row[0]

        conn.close()
        return post_id

    def add_worker(self, name: str, post: str, year: int) -> None:
        post_id = self.get_or_create_post(post)

        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO workers (worker_name, post_id, worker_year)
            VALUES (?, ?, ?)
            """,
            (name, post_id, year)
        )

        conn.commit()
        conn.close()

    def get_all_workers(self) -> list[Worker]:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT workers.worker_name, posts.post_title, workers.worker_year
            FROM workers
            INNER JOIN posts ON posts.post_id = workers.post_id
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            Worker(name=row[0], post=row[1], year=row[2])
            for row in rows
        ]

    def select_by_period(self, period: int) -> list[Worker]:
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT workers.worker_name, posts.post_title, workers.worker_year
            FROM workers
            INNER JOIN posts ON posts.post_id = workers.post_id
            WHERE (strftime('%Y', date('now')) - workers.worker_year) >= ?
            """,
            (period,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            Worker(name=row[0], post=row[1], year=row[2])
            for row in rows
        ]


# ===========================================================
#    ФУНКЦИЯ ДЛЯ ФОРМАТИРОВАНИЯ ВЫВОДА
# ===========================================================

def display_workers(workers: list[Worker]) -> None:
    if not workers:
        print("Список работников пуст.")
        return

    line = '+{}+{}+{}+{}+'.format(
        '-' * 6,
        '-' * 32,
        '-' * 22,
        '-' * 10
    )

    print(line)
    print('| {:^6} | {:^30} | {:^20} | {:^8} |'.format(
        "№", "Ф.И.О.", "Должность", "Год"
    ))
    print(line)

    for idx, w in enumerate(workers, 1):
        print('| {:^6} | {:^30} | {:^20} | {:^8} |'.format(
            idx, w.name, w.post, w.year
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
        default=str(Path.home() / "workers.db"),
        help="Имя файла базы данных"
    )

    # Основной парсер
    parser = argparse.ArgumentParser("workers")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command")

    # add
    add = subparsers.add_parser("add", parents=[file_parser], help="Добавить работника")
    add.add_argument("-n", "--name", required=True)
    add.add_argument("-p", "--post", required=True)
    add.add_argument("-y", "--year", required=True, type=int)

    # display
    subparsers.add_parser("display", parents=[file_parser], help="Показать всех")

    # select
    select = subparsers.add_parser("select", parents=[file_parser], help="Выборка по стажу")
    select.add_argument("-P", "--period", required=True, type=int)

    # Разбор аргументов
    args = parser.parse_args(command_line)

    # Работа с БД
    repo = StaffRepository(Path(args.db))

    if args.command == "add":
        repo.add_worker(args.name, args.post, args.year)
        print(f"Работник {args.name} успешно добавлен!")

    elif args.command == "display":
        display_workers(repo.get_all_workers())

    elif args.command == "select":
        display_workers(repo.select_by_period(args.period))


if __name__ == "__main__":
    main()