from sqlalchemy.orm import Session
from models import User
from utils import hash_password
from typing import Optional, List, Dict

import re
from sqlalchemy.orm import Session

def generate_user_id(db: Session) -> str:
    # Query the current highest User_ID (assumes it's in format 'USR' followed by digits)
    last_user = db.query(User).order_by(User.Users_ID.desc()).first()
    
    if last_user:
        # Extract the numeric part of the last User_ID
        match = re.match(r"USR(\d+)", last_user.Users_ID)
        if match:
            last_id = int(match.group(1))
            new_id = last_id + 1
        else:
            new_id = 1
    else:
        # If no users exist, start from 1
        new_id = 1

    # Return the new User_ID in the 'USR12345' format
    return f"USR{new_id:05d}"  # Formats the ID as 'USR00001', 'USR00002', etc.

def create_user(db: Session, user_data: dict) -> User:
    # Generate a unique User_ID before creating the user
    user_data['Users_ID'] = generate_user_id(db)
    
    # Create the new user with the provided data
    new_user = User(**user_data)
    
    # Add the user to the session and commit the transaction
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.Email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.Username == username).first()

def get_user_by_password(db: Session, password: str):
    return db.query(User).filter(User.Password == password).first()

def search_ingredients(
    nama: Optional[str] = None,
    benefit: Optional[str] = None,
    kategori: Optional[str] = None
) -> List[Dict]:
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM ingredients WHERE 1=1"
            params = []

            if nama:
                query += " AND nama LIKE %s"
                params.append(f"%{nama}%")
            if benefit:
                query += " AND FIND_IN_SET(%s, benefitidn)"
                params.append(benefit)
            if kategori:
                query += " AND FIND_IN_SET(%s, kategoriidn)"
                params.append(kategori)

            cursor.execute(query, params)
            results = cursor.fetchall()

            return results
    except Error as e:
        raise Exception(f"Database error: {str(e)}")
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)

            # Query dasar
            query = "SELECT * FROM ingredients WHERE 1=1"
            params = []

            # Filter berdasarkan nama
            if nama:
                query += " AND nama LIKE %s"
                params.append(f"%{nama}%")

            # Filter berdasarkan benefit
            if benefit:
                query += " AND FIND_IN_SET(%s, benefitidn)"
                params.append(benefit)

            # Filter berdasarkan kategori
            if kategori:
                query += " AND FIND_IN_SET(%s, kategoriidn)"
                params.append(kategori)

            # Eksekusi query
            cursor.execute(query, params)
            results = cursor.fetchall()

            return results

    except Error as e:
        raise Exception(f"Database error: {str(e)}")