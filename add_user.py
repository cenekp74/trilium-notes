#!/usr/bin/env python3
"""Script to add a user to the database."""
import sys
import getpass
from app import app, db, bcrypt
from app.db_classes import User


def add_user(username: str, password: str) -> None:
    with app.app_context():
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' added successfully (id={user.id}).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_user.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    password = getpass.getpass(f"Password for '{username}': ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)

    add_user(username, password)
