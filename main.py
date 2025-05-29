import sys
from PyQt6.QtWidgets import QApplication
from gui.dialogs.login_dialog import LoginDialog
from gui.main_window import MainWindow
from resources.theme import get_qss


def load_stylesheet(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(get_qss())

    while True:
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

    sys.exit(0)


if __name__ == "__main__":
    main()
