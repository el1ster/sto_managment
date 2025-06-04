import json
import os

SETTINGS_DIR = "resources"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "user_settings.json")


def load_settings() -> dict:
    """
    Завантажує словник налаштувань користувача з JSON-файлу.

    Returns:
        dict: Словник налаштувань, або порожній словник у разі помилки.
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_settings(settings: dict) -> None:
    """
    Зберігає словник налаштувань користувача у JSON-файл.

    Args:
        settings (dict): Словник налаштувань для збереження.
    """
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_setting(key: str, default=None):
    """
    Повертає значення для ключа key із налаштувань.

    Args:
        key (str): Ключ налаштування.
        default: Значення за замовчуванням, якщо ключ не знайдено.

    Returns:
        Будь-яке: Значення з налаштувань або default.
    """
    try:
        return load_settings().get(key, default)
    except Exception:
        return default


def set_setting(key: str, value) -> None:
    """
    Оновлює або додає налаштування з ключем key.

    Args:
        key (str): Ключ налаштування.
        value: Значення для збереження.
    """
    try:
        settings = load_settings()
        settings[key] = value
        save_settings(settings)
    except Exception:
        pass
