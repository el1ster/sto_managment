import json
import os

SETTINGS_DIR = "resources"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "user_settings.json")


def load_settings() -> dict:
    """
    Завантажує словник налаштувань користувача з JSON-файлу.
    Якщо файл не існує — повертає порожній словник.
    """
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def save_settings(settings: dict) -> None:
    """
    Зберігає словник налаштувань користувача у JSON-файл.
    """
    # Переконайся, що папка resources існує
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_setting(key: str, default=None):
    """
    Повертає значення для ключа key із налаштувань.
    """
    return load_settings().get(key, default)


def set_setting(key: str, value) -> None:
    """
    Оновлює або додає налаштування з ключем key.
    """
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
