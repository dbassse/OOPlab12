# test_zad1.py
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from zad1 import PetRepository, Owner, Pet, display_owners, display_pets


@pytest.fixture
def repo(temp_db):
    """Фикстура для репозитория с временной БД."""
    return PetRepository(temp_db)

def test_display_owners_empty(capsys):
    """Тест отображения пустого списка владельцев."""
    display_owners([])
    captured = capsys.readouterr()
    assert "Список владельцев пуст." in captured.out


def test_display_owners_non_empty(capsys):
    """Тест отображения непустого списка владельцев."""
    owners = [
        Owner(id=1, name="Иван Иванов", phone="+79991234567"),
        Owner(id=2, name="Анна Петрова", phone="+79992345678")
    ]
    display_owners(owners)
    captured = capsys.readouterr()
    
    assert "Иван Иванов" in captured.out
    assert "Анна Петрова" in captured.out
    assert "ID" in captured.out
    assert "Имя владельца" in captured.out
    assert "Телефон" in captured.out


def test_display_pets_empty(capsys):
    """Тест отображения пустого списка питомцев."""
    display_pets([])
    captured = capsys.readouterr()
    assert "Список животных пуст." in captured.out


def test_display_pets_non_empty(capsys):
    """Тест отображения непустого списка питомцев."""
    pets = [
        Pet(id=1, name="Барсик", species="Кошка", breed="Британская", age=3, owner_id=1),
        Pet(id=2, name="Шарик", species="Собака", breed="Овчарка", age=5, owner_id=2)
    ]
    display_pets(pets, show_owner=True)
    captured = capsys.readouterr()
    
    assert "Барсик" in captured.out
    assert "Шарик" in captured.out
    assert "Кошка" in captured.out
    assert "Собака" in captured.out
    assert "ID" in captured.out
    assert "Кличка" in captured.out
    assert "Вид" in captured.out
