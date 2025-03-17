import pytest
from bot.utils import clean_price_string

def test_clean_price_string_valid():
    assert clean_price_string("1 234,56 ₽") == 1234.56
    assert clean_price_string("1234.56 USD") == 1234.56
    assert clean_price_string("1234") == 1234.0
    assert clean_price_string("1,234,567.89") == 1234567.89 # Проверка на корректную обработку больших чисел

def test_clean_price_string_invalid():
    assert clean_price_string("Цена не указана") is None
    assert clean_price_string("abc") is None
    assert clean_price_string("") is None

# Можно добавить тесты для database.py и handlers, если будет время.