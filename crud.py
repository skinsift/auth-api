from sqlalchemy.orm import Session
from models import User
from utils import hash_password

import re
from sqlalchemy.orm import Session

def generate_user_id(db: Session) -> str:
    # Query the current highest User_ID (assumes it's in format 'USR' followed by digits)
    last_user = db.query(User).order_by(User.User_ID.desc()).first()
    
    if last_user:
        # Extract the numeric part of the last User_ID
        match = re.match(r"USR(\d+)", last_user.User_ID)
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

def create_user(db: Session, user_data):
    # Generate a new user ID
    new_user_id = generate_user_id(db)
    
    # Hash the password
    hashed_password = hash_password(user_data.Password)
    
    # Create the new user
    new_user = User(
        User_ID=new_user_id,  # Use the generated User_ID
        Username=user_data.Username,
        Password=hashed_password,
        Email=user_data.Email,
        Jenis_Kulit=user_data.Jenis_Kulit,
        Good_Ingre=user_data.Good_Ingre,
        Bad_Ingre=user_data.Bad_Ingre
    )
    
    # Add the user to the database
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
