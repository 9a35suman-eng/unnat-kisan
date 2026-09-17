from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, BulkBuyer
from admin_auth import get_current_user


# =========================================
# VERIFIED BULK BUYER ONLY
# =========================================

def get_current_verified_buyer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user.role != "bulk_buyer":
        raise HTTPException(
            status_code=403,
            detail="Bulk Buyer access required"
        )

    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.user_id == current_user.id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk Buyer profile not found"
        )

    if buyer.verification_status != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail="Bulk Buyer account is not verified by Admin"
        )

    return buyer