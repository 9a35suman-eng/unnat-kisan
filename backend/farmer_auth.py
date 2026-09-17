from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Farmer
from admin_auth import get_current_user


def get_current_farmer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "farmer":
        raise HTTPException(
            status_code=403,
            detail="Farmer access required"
        )

    farmer = db.query(Farmer).filter(
        Farmer.user_id == current_user.id
    ).first()

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer profile not found"
        )

    return farmer