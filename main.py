"""Punto de entrada de SAINT REPAIRS."""

from database.database import init_db
from app import App, Login


def main():
    init_db()
    login = Login()
    login.mainloop()
    if login.authenticated:
        app = App(login.user_id, login.user_name)
        app.mainloop()


if __name__ == "__main__":
    main()
