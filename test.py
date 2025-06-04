from models.user import User
from logic.password_service import hash_password
from models.db import db

test_users = [
    {"username": "superadmin", "password": "SuperPass1!", "role_id": 1},
    {"username": "admin01", "password": "AdminPass1!", "role_id": 2},
    {"username": "accountant01", "password": "AccPass1!", "role_id": 4},
    {"username": "accountant02", "password": "AccPass2!", "role_id": 4},
    {"username": "master01", "password": "MasterPass1!", "role_id": 5},
    {"username": "master02", "password": "MasterPass2!", "role_id": 5},
    {"username": "master03", "password": "MasterPass3!", "role_id": 5},
    {"username": "master04", "password": "MasterPass4!", "role_id": 5},
    {"username": "mech01", "password": "MechPass1!", "role_id": 6},
    {"username": "mech02", "password": "MechPass2!", "role_id": 6},
    {"username": "mech03", "password": "MechPass3!", "role_id": 6},
    {"username": "mech04", "password": "MechPass4!", "role_id": 6},
    {"username": "mech05", "password": "MechPass5!", "role_id": 6},
    {"username": "mech06", "password": "MechPass6!", "role_id": 6},
    {"username": "mech07", "password": "MechPass7!", "role_id": 6},
    {"username": "mech08", "password": "MechPass8!", "role_id": 6},
]

def create_test_users():
    with db.atomic():
        for u in test_users:
            existing = User.get_or_none(User.username == u["username"])
            if existing:
                print(f"[!] Користувач '{u['username']}' вже існує.")
                continue

            User.create(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                role_id=u["role_id"],
                is_active=True,
                last_login=None
            )
            print(f"[+] Додано користувача: {u['username']} (роль ID: {u['role_id']})")

    print("\n[✓] Всі користувачі створені.")

if __name__ == "__main__":
    create_test_users()
