from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, BulkBuyer
from admin_auth import get_current_admin
from auth import hash_password
from datetime import datetime


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


# =========================================
# GET PENDING BULK BUYERS
# =========================================

@router.get("/bulk-buyers/pending")
def get_pending_bulk_buyers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    buyers = db.query(BulkBuyer).filter(
        BulkBuyer.verification_status == "PENDING"
    ).all()

    result = []

    for buyer in buyers:

        user = db.query(User).filter(
            User.id == buyer.user_id
        ).first()

        result.append({
            "bulk_buyer_id": buyer.id,
            "user_id": buyer.user_id,
            "business_name": buyer.business_name,
            "contact_person": buyer.contact_person,
            "mobile": user.mobile if user else None,
            "email": user.email if user else None,
            "business_type": buyer.business_type,
            "product_category": buyer.product_category,
            "monthly_requirement": buyer.monthly_requirement,
            "state": user.state if user else None,
            "district": user.district if user else None,
            "city_village": user.city_village if user else None,
            "license_number": buyer.license_number,
            "license_photo": f"/uploads/licenses/{buyer.license_photo.split('/')[-1]}",
            "verification_status": buyer.verification_status,
            "created_at": user.created_at if user else None
        })

    return {
        "count": len(result),
        "buyers": result
    }
    # =========================================
# GET SINGLE BULK BUYER DETAILS
# =========================================

@router.get("/bulk-buyers/{buyer_id}")
def get_bulk_buyer_details(
    buyer_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk Buyer not found"
        )

    user = db.query(User).filter(
        User.id == buyer.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Associated user not found"
        )

    return {
        "bulk_buyer_id": buyer.id,
        "user_id": buyer.user_id,

        "business_name": buyer.business_name,
        "contact_person": buyer.contact_person,
        "mobile": user.mobile,
        "email": user.email,

        "business_type": buyer.business_type,
        "product_category": buyer.product_category,
        "monthly_requirement": buyer.monthly_requirement,

        "state": user.state,
        "district": user.district,
        "city_village": user.city_village,

        "license_number": buyer.license_number,

        "license_photo": (
            f"/uploads/licenses/"
            f"{buyer.license_photo.split('/')[-1]}"
        ),

        "verification_status": buyer.verification_status,
        "rejection_reason": buyer.rejection_reason,

        "created_at": user.created_at,
        "verified_by": buyer.verified_by,
        "verified_at": buyer.verified_at
    }
    # =========================================
# APPROVE BULK BUYER
# =========================================

@router.put("/bulk-buyers/{buyer_id}/approve")
def approve_bulk_buyer(
    buyer_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk Buyer not found"
        )

    if buyer.verification_status == "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Bulk Buyer is already approved"
        )

    buyer.verification_status = "APPROVED"
    buyer.rejection_reason = None
    buyer.verified_by = admin.id
    buyer.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(buyer)

    return {
        "message": "Bulk Buyer approved successfully",
        "bulk_buyer_id": buyer.id,
        "verification_status": buyer.verification_status,
        "verified_by": buyer.verified_by,
        "verified_at": buyer.verified_at
    }
    # =========================================
# REJECT BULK BUYER
# =========================================

@router.put("/bulk-buyers/{buyer_id}/reject")
def reject_bulk_buyer(
    buyer_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk Buyer not found"
        )

    if buyer.verification_status == "REJECTED":
        raise HTTPException(
            status_code=400,
            detail="Bulk Buyer is already rejected"
        )

    if not rejection_reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required"
        )

    buyer.verification_status = "REJECTED"
    buyer.rejection_reason = rejection_reason
    buyer.verified_by = admin.id
    buyer.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(buyer)

    return {
        "message": "Bulk Buyer rejected successfully",
        "bulk_buyer_id": buyer.id,
        "verification_status": buyer.verification_status,
        "rejection_reason": buyer.rejection_reason,
        "verified_by": buyer.verified_by,
        "verified_at": buyer.verified_at
    }
    # =========================================
# CREATE ADMIN - DEVELOPMENT ONLY
# =========================================

@router.post("/create-admin")
def create_admin(
    db: Session = Depends(get_db)
):

    existing_admin = db.query(User).filter(
        User.role == "admin"
    ).first()

    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin already exists"
        )

    admin = User(
        full_name="Unnat Kisan Admin",
        mobile="9999999999",
        email="admin@unnatkisan.com",
        password_hash=hash_password("Admin@12345"),
        role="admin",
        state="Uttar Pradesh",
        district="Kanpur",
        city_village="Admin Office"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return {
        "message": "Admin created successfully",
        "admin_id": admin.id,
        "email": admin.email,
        "role": admin.role
    }

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from admin_auth import get_current_admin
from models import BulkBuyer


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


@router.get("/bulk-buyers/pending")
def get_pending_buyers(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buyers = db.query(BulkBuyer).filter(
        BulkBuyer.verification_status == "PENDING"
    ).all()

    return [
        {
            "id": buyer.id,
            "business_name": buyer.business_name,
            "contact_person": buyer.contact_person,
            "business_type": buyer.business_type,
            "product_category": buyer.product_category,
            "monthly_requirement": buyer.monthly_requirement,
            "license_number": buyer.license_number,
            "license_photo": buyer.license_photo,
            "verification_status": buyer.verification_status
        }
        for buyer in buyers
    ]


@router.patch("/bulk-buyers/{buyer_id}/approve")
def approve_bulk_buyer(
    buyer_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk buyer not found"
        )

    buyer.verification_status = "APPROVED"
    buyer.rejection_reason = None
    buyer.verified_by = admin.id
    buyer.verified_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Bulk buyer approved successfully",
        "buyer_id": buyer.id,
        "status": buyer.verification_status
    }


@router.patch("/bulk-buyers/{buyer_id}/reject")
def reject_bulk_buyer(
    buyer_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buyer = db.query(BulkBuyer).filter(
        BulkBuyer.id == buyer_id
    ).first()

    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Bulk buyer not found"
        )

    buyer.verification_status = "REJECTED"
    buyer.rejection_reason = rejection_reason
    buyer.verified_by = admin.id
    buyer.verified_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Bulk buyer rejected",
        "buyer_id": buyer.id,
        "status": buyer.verification_status,
        "reason": rejection_reason
    }

@router.get("/payments/pending")
def get_pending_payments(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    payments = db.query(Payment).filter(
        Payment.status == "PROOF_UPLOADED"
    ).all()

    result = []

    for payment in payments:

        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == payment.order_id
        ).first()

        if not order:
            continue

        result.append({
            "payment_id": payment.id,
            "order_id": order.id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "payment_proof": payment.payment_proof,
            "status": payment.status
        })

    return result

@router.patch("/payments/{payment_id}/verify")
def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if payment.status != "PROOF_UPLOADED":
        raise HTTPException(
            status_code=400,
            detail="Payment is not awaiting verification"
        )

    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == payment.order_id
    ).first()

    payment.status = "VERIFIED"
    payment.verified_by = admin.id
    payment.verified_at = datetime.utcnow()

    if order:
        order.status = "COMPLETED"

    db.commit()

    return {
        "message": "Payment verified successfully",
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "status": "VERIFIED"
    }

@router.patch("/payments/{payment_id}/reject")
def reject_payment(
    payment_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    payment.status = "REJECTED"

    db.commit()

    return {
        "message": "Payment rejected",
        "payment_id": payment.id,
        "reason": reason
    }

