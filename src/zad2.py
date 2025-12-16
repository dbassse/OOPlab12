#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from dataclasses import dataclass
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# ================================
#    МОДЕЛИ ДАННЫХ (DATACLASSES)
# ================================

@dataclass(frozen=True)
class OwnerData:
    id: int
    name: str
    phone: str


@dataclass(frozen=True)
class PetData:
    id: int
    name: str
    species: str
    breed: str
    age: int
    owner_id: int


# ================================
#    МОДЕЛИ SQLALCHEMY
# ================================

Base = declarative_base()


class OwnerModel(Base):
    __tablename__ = 'owners'
    
    id = Column('owner_id', Integer, primary_key=True)
    name = Column('owner_name', String, nullable=False)
    phone = Column('owner_phone', String, nullable=False)
    
    pets = relationship("PetModel", back_populates="owner", cascade="all, delete-orphan")


class PetModel(Base):
    __tablename__ = 'pets'
    
    id = Column('pet_id', Integer, primary_key=True)
    name = Column('pet_name', String, nullable=False)
    species = Column('pet_species', String, nullable=False)
    breed = Column('pet_breed', String, nullable=False)
    age = Column('pet_age', Integer, nullable=False)
    owner_id = Column('owner_id', Integer, ForeignKey('owners.owner_id'), nullable=False)
    
    owner = relationship("OwnerModel", back_populates="pets")


# ================================
#    РЕПОЗИТОРИЙ ДЛЯ РАБОТЫ С БД
# ================================

class PetRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_owner(self, name: str, phone: str) -> None:
        with self.Session() as session:
            owner = OwnerModel(name=name, phone=phone)
            session.add(owner)
            session.commit()

    def add_pet(self, name: str, species: str, breed: str, age: int, owner_id: int) -> None:
        with self.Session() as session:
            # Проверяем существование владельца
            owner = session.query(OwnerModel).filter_by(id=owner_id).first()
            if not owner:
                raise ValueError(f"Владелец с ID {owner_id} не найден")
            
            pet = PetModel(
                name=name,
                species=species,
                breed=breed,
                age=age,
                owner_id=owner_id
            )
            session.add(pet)
            session.commit()

    def get_all_owners(self) -> list[OwnerData]:
        with self.Session() as session:
            owners = session.query(OwnerModel).order_by(OwnerModel.name).all()
            return [
                OwnerData(id=owner.id, name=owner.name, phone=owner.phone)
                for owner in owners
            ]

    def get_all_pets(self) -> list[PetData]:
        with self.Session() as session:
            pets = session.query(PetModel).order_by(PetModel.name).all()
            return [
                PetData(
                    id=pet.id,
                    name=pet.name,
                    species=pet.species,
                    breed=pet.breed,
                    age=pet.age,
                    owner_id=pet.owner_id
                )
                for pet in pets
            ]

    def get_pets_by_owner(self, owner_id: int) -> list[PetData]:
        with self.Session() as session:
            # Проверяем существование владельца
            owner = session.query(OwnerModel).filter_by(id=owner_id).first()
            if not owner:
                raise ValueError(f"Владелец с ID {owner_id} не найден")
            
            pets = session.query(PetModel).filter_by(owner_id=owner_id).order_by(PetModel.name).all()
            return [
                PetData(
                    id=pet.id,
                    name=pet.name,
                    species=pet.species,
                    breed=pet.breed,
                    age=pet.age,
                    owner_id=pet.owner_id
                )
                for pet in pets
            ]

    def get_owner_by_id(self, owner_id: int) -> OwnerData | None:
        with self.Session() as session:
            owner = session.query(OwnerModel).filter_by(id=owner_id).first()
            if owner:
                return OwnerData(id=owner.id, name=owner.name, phone=owner.phone)
            return None


# ===========================================================
#    ФУНКЦИИ ДЛЯ ФОРМАТИРОВАННОГО ВЫВОДА
# ===========================================================

def display_owners(owners: list[OwnerData]) -> None:
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


def display_pets(pets: list[PetData], show_owner: bool = False) -> None:
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
        default=str(Path.home() / "pets_alchemy.db"),
        help="Путь к файлу базы данных"
    )

    # Основной парсер
    parser = argparse.ArgumentParser(
        "pets_alchemy",
        description="Система учета домашних животных (SQLAlchemy версия)"
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
        except Exception as e:
            print(f"Ошибка при добавлении владельца: {e}")

    elif args.command == "add_pet":
        try:
            repo.add_pet(args.name, args.species, args.breed, args.age, args.owner)
            print(f"Животное '{args.name}' успешно добавлено!")
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Ошибка при добавлении животного: {e}")

    elif args.command == "display_owners":
        try:
            owners = repo.get_all_owners()
            display_owners(owners)
        except Exception as e:
            print(f"Ошибка при получении списка владельцев: {e}")

    elif args.command == "display_pets":
        try:
            pets = repo.get_all_pets()
            display_pets(pets, show_owner=True)
        except Exception as e:
            print(f"Ошибка при получении списка животных: {e}")

    elif args.command == "select_pets_by_owner":
        try:
            owner = repo.get_owner_by_id(args.owner)
            if not owner:
                print(f"Ошибка: Владелец с ID {args.owner} не найден!")
                return

            pets = repo.get_pets_by_owner(args.owner)
            print(f"Животные владельца '{owner.name}' (ID: {owner.id}):")
            display_pets(pets, show_owner=False)
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Ошибка при выборке животных: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()