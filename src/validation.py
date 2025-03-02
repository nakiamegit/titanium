from config_manager import get_config

def validate_number(value, validate_range=None, validate_positive=False):
    """Валидирует числовые значения."""
    config = get_config()

    if not value:
        return config.get("Error", "error_empty_field")

    try:
        number = float(value)

        # Преобразуем строковые параметры обратно в нужные типы
        if validate_range and isinstance(validate_range, str):
            validate_range = tuple(map(float, validate_range.strip("()").split(",")))

        # Проверяем положительность, если это необходимо
        if validate_positive and number <= 0:
            return config.get("Error", "error_positive_number")

        # Проверяем диапазон, если он указан
        if validate_range:
            min_val, max_val = validate_range
            if not (min_val <= number <= max_val):
                error_message = config.get("Error", "error_invalid_range_base")
                return error_message.format(min=min_val, max=max_val)

        return True  # Данные корректны

    except ValueError:
        return config.get("Error", "error_invalid_number")