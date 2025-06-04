import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.dialogs.login_dialog import LoginDialog
from gui.main_window import MainWindow
from resources.theme import get_qss


def load_stylesheet(path: str) -> str:
    """
    Завантажує QSS-файл для стилів інтерфейсу.

    Args:
        path (str): Шлях до QSS-файлу.

    Returns:
        str: Вміст стилів.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(get_qss())

        while True:
            try:
                login_dialog = LoginDialog()
                res = login_dialog.exec()
                if res != LoginDialog.DialogCode.Accepted:
                    break

                current_user = login_dialog.user
                main_window = MainWindow(current_user)
                main_window.show()
                app.exec()

                if not getattr(main_window, "logout_requested", False):
                    break

            except Exception as inner_ex:
                QMessageBox.critical(None, "Помилка", f"Сталася помилка під час запуску вікна:\n{inner_ex}")
                break

        sys.exit(0)

    except Exception as ex:
        # Якщо QApplication ще не створено або помилка поза вікном — друкуємо у консоль
        print(f"Критична помилка запуску програми: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
