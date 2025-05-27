# main.py

import sys
from PyQt6.QtWidgets import QApplication
from gui.dialogs.login_dialog import LoginDialog
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Діалог входу (login)
    login_dialog = LoginDialog()
    if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
        current_user = login_dialog.user  # отримуємо авторизованого користувача

        # Передаємо current_user у MainWindow
        window = MainWindow(current_user)
        window.show()
        sys.exit(app.exec())
    else:
        # Якщо логін неуспішний або відмінено — вихід
        sys.exit(0)


if __name__ == "__main__":
    main()
