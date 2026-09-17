import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from buyer_auth import get_current_verified_buyer

from models import (
    BuyerRequirement,
    CropListing,
    PurchaseRequest,
    QualityInspection,
    PurchaseOrder
)

from schemas import (
    BuyerRequirementCreate,
    PurchaseRequestCreate
)
import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from models import Payment, PurchaseOrder

router = APIRouter(
    prefix="/api/buyer",
    tags=["Bulk Buyer"]
)


@router.get("/test-access")
def test_buyer_access(
    buyer=Depends(get_current_verified_buyer)
):

    return {
        "message": "Verified Bulk Buyer access granted",
        "bulk_buyer_id": buyer.id,
        "business_name": buyer.business_name,
        "verification_status": buyer.verification_status
    }

@router.post("/requirements")
def create_requirement(
    data: BuyerRequirementCreate,
    buyer=Depends(get_current_verified_buyer),
    db: Session = Depends(get_db)
):

    requirement = BuyerRequirement(
        buyer_id=buyer.id,
        product_name=data.product_name,
        quantity=data.quantity,
        quantity_unit=data.quantity_unit,
        expected_price=data.expected_price,
        required_by=data.required_by,
        state=data.state,
        district=data.district,
        city=data.city,
        description=data.description,
        status="OPEN"
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return {
        "message": "Buyer requirement created successfully",
        "requirement_id": requirement.id,
        "status": requirement.status
    }

# =========================================================
# VIEW FARMER CROP LISTINGS
# ONLY VERIFIED BULK BUYERS
# =========================================================

@router.get("/crops")
def get_available_farmer_crops(
    buyer=Depends(get_current_verified_buyer),
    db: Session = Depends(get_db)
):

    crops = db.query(CropListing).filter(
        CropListing.status == "AVAILABLE"
    ).order_by(
        CropListing.created_at.desc()
    ).all()

    return {
        "message": "Available farmer crops fetched successfully",
        "count": len(crops),
        "crops": [
            {
                "id": crop.id,
                "crop_name": crop.crop_name,
                "harvest_date": crop.harvest_date,
                "quality_grade": crop.quality_grade,
                "quantity": crop.quantity,
                "quantity_unit": crop.quantity_unit,
                "expected_price_per_kg": crop.expected_price_per_kg,

                "state": crop.state,
                "district": crop.district,
                "city": crop.city,

                "description": crop.description,

                "photos": json.loads(
                    crop.photos or "[]"
                ),

                "status": crop.status,
                "created_at": crop.created_at
            }
            for crop in crops
        ]
    }

@router.post("/purchase-requests")
def create_purchase_request(
    request: PurchaseRequestCreate,
    buyer=Depends(get_current_verified_buyer),
    db: Session = Depends(get_db)
):
    # Check crop exists
    crop = db.query(CropListing).filter(
        CropListing.id == request.crop_id
    ).first()

    if not crop:
        raise HTTPException(
            status_code=404,
            detail="Crop listing not found"
        )

    # Crop must be available
    if crop.status != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="This crop is no longer available"
        )

    # Requested quantity cannot exceed available quantity
    if request.requested_quantity > crop.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {crop.quantity} {crop.quantity_unit} is available"
        )

    # Create purchase request
    purchase_request = PurchaseRequest(
        crop_id=crop.id,
        buyer_id=buyer.id,
        requested_quantity=request.requested_quantity,
        offered_price_per_kg=request.offered_price_per_kg,
        message=request.message,
        status="PENDING"
    )

    db.add(purchase_request)
    db.commit()
    db.refresh(purchase_request)

    return {
        "message": "Purchase request sent successfully",
        "request_id": purchase_request.id,
        "crop_id": crop.id,
        "crop_name": crop.crop_name,
        "requested_quantity": purchase_request.requested_quantity,
        "offered_price_per_kg": purchase_request.offered_price_per_kg,
        "status": purchase_request.status
    }

@router.get("/quality-checked-requests")
def get_quality_checked_requests(
    db: Session = Depends(get_db),
    buyer=Depends(get_current_verified_buyer)
):
    requests = (
        db.query(PurchaseRequest)
        .filter(
            PurchaseRequest.buyer_id == buyer.id,
            PurchaseRequest.status == "QUALITY_CHECKED"
        )
        .all()
    )

    result = []

    for request in requests:

        crop = db.query(CropListing).filter(
            CropListing.id == request.crop_id
        ).first()

        inspection = db.query(QualityInspection).filter(
            QualityInspection.purchase_request_id == request.id
        ).first()

        if not inspection:
            continue

        result.append({
            "request_id": request.id,
            "crop_name": crop.crop_name if crop else None,
            "requested_quantity": request.requested_quantity,
            "offered_price_per_kg": request.offered_price_per_kg,

            "quality_grade": inspection.quality_grade,
            "quantity_approved": inspection.quantity_approved,
            "inspection_status": inspection.status,
            "remarks": inspection.remarks,

            "status": request.status
        })

    return result


@router.post("/purchase-requests/{request_id}/confirm")
def confirm_purchase(
    request_id: int,
    db: Session = Depends(get_db),
    buyer=Depends(get_current_verified_buyer)
):
    request = db.query(PurchaseRequest).filter(
        PurchaseRequest.id == request_id,
        PurchaseRequest.buyer_id == buyer.id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Purchase request not found"
        )

    if request.status != "QUALITY_CHECKED":
        raise HTTPException(
            status_code=400,
            detail="Purchase can be confirmed only after quality inspection"
        )

    inspection = db.query(QualityInspection).filter(
        QualityInspection.purchase_request_id == request.id
    ).first()

    if not inspection:
        raise HTTPException(
            status_code=400,
            detail="Quality inspection not found"
        )

    if inspection.status != "PASSED":
        raise HTTPException(
            status_code=400,
            detail="Purchase cannot be confirmed because quality inspection failed"
        )

    crop = db.query(CropListing).filter(
        CropListing.id == request.crop_id
    ).first()

    if not crop:
        raise HTTPException(
            status_code=404,
            detail="Crop not found"
        )

    total_amount = (
        inspection.quantity_approved *
        request.offered_price_per_kg
    )

    order = PurchaseOrder(
        purchase_request_id=request.id,
        farmer_id=crop.farmer_id,
        buyer_id=buyer.id,
        crop_id=crop.id,
        quantity=inspection.quantity_approved,
        quantity_unit=crop.quantity_unit,
        price_per_kg=request.offered_price_per_kg,
        total_amount=total_amount,
        status="PAYMENT_PENDING"
    )

    db.add(order)

    request.status = "PURCHASE_CONFIRMED"

    db.commit()
    db.refresh(order)

    return {
        "message": "Purchase confirmed successfully",
        "order_id": order.id,
        "total_amount": total_amount,
        "status": order.status,
        "next_step": "Payment"
    }

@router.post("/orders/{order_id}/payment-proof")
async def upload_payment_proof(
    order_id: int,
    payment_method: str,
    proof: UploadFile = File(...),
    db: Session = Depends(get_db),
    buyer=Depends(get_current_verified_buyer)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == order_id,
        PurchaseOrder.buyer_id == buyer.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != "PAYMENT_PENDING":
        raise HTTPException(
            status_code=400,
            detail="Payment proof cannot be uploaded at this stage"
        )

    allowed_types = [
        "image/jpeg",
        "image/png",
        "application/pdf"
    ]

    if proof.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG or PDF files are allowed"
        )

    os.makedirs("upload/payment_proofs", exist_ok=True)

    extension = os.path.splitext(proof.filename)[1]

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        "upload/payment_proofs",
        filename
    )

    contents = await proof.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment_method,
        payment_proof=file_path,
        status="PROOF_UPLOADED"
    )

    db.add(payment)

    order.status = "PAYMENT_PROOF_UPLOADED"

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment proof uploaded successfully",
        "payment_id": payment.id,
        "order_id": order.id,
        "amount": order.total_amount,
        "status": "PROOF_UPLOADED",
        "next_step": "Admin verification"
    }