import re

def clean_price_string(price_string):
    """Очищает строку с ценой от лишних символов (пробелов, валют)."""
    price_string = price_string.replace(" ", "") # Удаляем пробелы
    price_string = re.sub(r'[^\d.,]', '', price_string) # Удаляем все, кроме цифр, точек и запятых
    price_string = price_string.replace(",", ".") # Заменяем запятые на точки для float
    try:
        return float(price_string)
    except ValueError:
        return None # Возвращаем None, если не удалось преобразовать в число