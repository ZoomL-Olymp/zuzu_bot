import re

def clean_price_string(price_string):
    """Очищает строку с ценой от лишних символов (пробелов, валют)."""
    price_string = price_string.replace(" ", "")  # Удаляем пробелы
    price_string = re.sub(r'[^\d,.]', '', price_string)  # Удаляем все, кроме цифр, точек и запятых

    # Сначала заменяем все запятые на точки
    price_string = price_string.replace(",", ".")

    #Удаляем все точки, кроме последней (если точек несколько)
    if price_string.count('.') > 1:
        parts = price_string.split('.')
        price_string = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(price_string)
    except ValueError:
        return None