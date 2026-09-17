import os
import uuid
import json

from datetime import date, datetime
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlalchemy.orm import Session

from database import get_db
from models import (
    BuyerRequirement,
    CropListing,
    PurchaseRequest,
    QualityInspection,
    Farmer
)
from farmer_auth import get_current_farmer


router = APIRouter(
    prefix="/api/farmer",
    tags=["farmer"]
)


# =========================================================
# GET OPEN BUYER REQUIREMENTS
# =========================================================

@router.get("/buyer-requirements")
def get_buyer_requirements(
    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    requirements = db.query(BuyerRequirement).filter(
        BuyerRequirement.status == "OPEN"
    ).order_by(
        BuyerRequirement.created_at.desc()
    ).all()

    return {
        "message": "Open buyer requirements fetched successfully",
        "count": len(requirements),
        "requirements": [
            {
                "id": requirement.id,
                "product_name": requirement.product_name,
                "quantity": requirement.quantity,
                "quantity_unit": requirement.quantity_unit,
                "expected_price": requirement.expected_price,
                "required_by": requirement.required_by,
                "state": requirement.state,
                "district": requirement.district,
                "city": requirement.city,
                "description": requirement.description,
                "status": requirement.status,
                "created_at": requirement.created_at
            }
            for requirement in requirements
        ]
    }


# =========================================================
# CREATE CROP LISTING
# =========================================================

@router.post("/crops")
async def create_crop_listing(

    crop_name: str = Form(...),
    harvest_date: date = Form(...),
    quality_grade: str = Form(...),

    quantity: float = Form(...),
    quantity_unit: str = Form("kg"),

    expected_price_per_kg: float = Form(...),

    state: str = Form(...),
    district: str = Form(...),
    city: str = Form(...),

    description: str = Form(None),

    photos: list[UploadFile] = File(default=[]),

    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Basic validation
    # -----------------------------

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    if expected_price_per_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Expected price must be greater than 0"
        )

    # -----------------------------
    # Quality grade validation
    # -----------------------------

    allowed_grades = [
        "A",
        "B",
        "C",
        "PREMIUM",
        "GOOD",
        "AVERAGE"
    ]

    quality_grade = quality_grade.upper().strip()

    if quality_grade not in allowed_grades:
        raise HTTPException(
            status_code=400,
            detail="Invalid quality grade. Use A, B, C, PREMIUM, GOOD or AVERAGE."
        )

    # -----------------------------
    # Photo upload
    # -----------------------------

    upload_directory = "upload/crops"

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    photo_urls = []

    # Maximum 5 photos
    if len(photos) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 crop photos are allowed."
        )

    allowed_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    for photo in photos:

        if not photo.filename:
            continue

        extension = os.path.splitext(
            photo.filename
        )[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        filename = (
            f"{uuid.uuid4()}{extension}"
        )

        file_path = os.path.join(
            upload_directory,
            filename
        )

        content = await photo.read()

        # 5 MB maximum per image
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"{photo.filename} is larger than 5 MB."
            )

        with open(file_path, "wb") as file:
            file.write(content)

        photo_urls.append(
            f"/upload/crops/{filename}"
        )

    # -----------------------------
    # Create listing
    # -----------------------------

    crop = CropListing(
        farmer_id=farmer.id,
        crop_name=crop_name,
        harvest_date=harvest_date,
        quality_grade=quality_grade,
        quantity=quantity,
        quantity_unit=quantity_unit,
        expected_price_per_kg=expected_price_per_kg,
        state=state,
        district=district,
        city=city,
        description=description,
        photos=json.dumps(photo_urls),
        status="AVAILABLE"
    )

    db.add(crop)
    db.commit()
    db.refresh(crop)

    return {
        "message": "Crop listed successfully",
        "crop_id": crop.id,
        "crop_name": crop.crop_name,
        "quality_grade": crop.quality_grade,
        "quantity": crop.quantity,
        "quantity_unit": crop.quantity_unit,
        "expected_price_per_kg": crop.expected_price_per_kg,
        "photos": photo_urls,
        "status": crop.status
    }


# =========================================================
# FARMER'S OWN CROP LISTINGS
# =========================================================

@router.get("/crops")
def get_my_crops(
    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    crops = db.query(CropListing).filter(
        CropListing.farmer_id == farmer.id
    ).order_by(
        CropListing.created_at.desc()
    ).all()

    return {
        "message": "Your crop listings fetched successfully",
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
                "photos": json.loads(crop.photos or "[]"),
                "status": crop.status,
                "created_at": crop.created_at
            }
            for crop in crops
        ]
    }

# =========================================================
# FARMER - INCOMING PURCHASE REQUESTS
# =========================================================

@router.get("/purchase-requests")
def get_incoming_purchase_requests(
    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    requests = (
        db.query(PurchaseRequest, CropListing)
        .join(
            CropListing,
            PurchaseRequest.crop_id == CropListing.id
        )
        .filter(
            CropListing.farmer_id == farmer.id
        )
        .order_by(
            PurchaseRequest.created_at.desc()
        )
        .all()
    )

    return {
        "message": "Incoming purchase requests fetched successfully",
        "count": len(requests),
        "requests": [
            {
                "request_id": request.id,
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "requested_quantity": request.requested_quantity,
                "quantity_unit": crop.quantity_unit,
                "offered_price_per_kg": request.offered_price_per_kg,
                "total_amount": (
                    request.requested_quantity *
                    request.offered_price_per_kg
                ),
                "message": request.message,
                "status": request.status,
                "farmer_response": request.farmer_response,
                "created_at": request.created_at,
                "responded_at": request.responded_at
            }
            for request, crop in requests
        ]
    }

# =========================================================
# FARMER - ACCEPT PURCHASE REQUEST
# =========================================================

@router.patch("/purchase-requests/{request_id}/accept")
def accept_purchase_request(
    request_id: int,
    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    purchase_request = db.query(PurchaseRequest).filter(
        PurchaseRequest.id == request_id
    ).first()

    if not purchase_request:
        raise HTTPException(
            status_code=404,
            detail="Purchase request not found"
        )

    crop = db.query(CropListing).filter(
        CropListing.id == purchase_request.crop_id
    ).first()

    if not crop or crop.farmer_id != farmer.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized for this request"
        )

    if purchase_request.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="This request has already been processed"
        )

    if purchase_request.requested_quantity > crop.quantity:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity is no longer available"
        )

    purchase_request.status = "ACCEPTED"
    purchase_request.farmer_response = "Purchase request accepted"
    purchase_request.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(purchase_request)

    return {
        "message": "Purchase request accepted successfully",
        "request_id": purchase_request.id,
        "status": purchase_request.status,
        "next_step": "Buyer can inspect crop quality before payment"
    }


# =========================================================
# FARMER - REJECT PURCHASE REQUEST
# =========================================================

@router.patch("/purchase-requests/{request_id}/reject")
def reject_purchase_request(
    request_id: int,
    farmer=Depends(get_current_farmer),
    db: Session = Depends(get_db)
):

    purchase_request = db.query(PurchaseRequest).filter(
        PurchaseRequest.id == request_id
    ).first()

    if not purchase_request:
        raise HTTPException(
            status_code=404,
            detail="Purchase request not found"
        )

    crop = db.query(CropListing).filter(
        CropListing.id == purchase_request.crop_id
    ).first()

    if not crop or crop.farmer_id != farmer.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized for this request"
        )

    if purchase_request.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="This request has already been processed"
        )

    purchase_request.status = "REJECTED"
    purchase_request.farmer_response = "Purchase request rejected"
    purchase_request.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(purchase_request)

    return {
        "message": "Purchase request rejected",
        "request_id": purchase_request.id,
        "status": purchase_request.status
    }

@router.post("/purchase-requests/{request_id}/inspection")
def create_quality_inspection(
    request_id: int,
    quality_grade: str,
    quantity_approved: float,
    remarks: str = "",
    db: Session = Depends(get_db),
    farmer: Farmer = Depends(get_current_farmer)
):
    purchase_request = db.query(PurchaseRequest).filter(
        PurchaseRequest.id == request_id
    ).first()

    if not purchase_request:
        raise HTTPException(
            status_code=404,
            detail="Purchase request not found"
        )

    crop = db.query(CropListing).filter(
        CropListing.id == purchase_request.crop_id
    ).first()

    if not crop or crop.farmer_id != farmer.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot inspect this request"
        )

    # Inspection only after farmer accepts
    if purchase_request.status != "ACCEPTED":
        raise HTTPException(
            status_code=400,
            detail="Quality inspection is allowed only after request acceptance"
        )

    if quantity_approved <= 0:
        raise HTTPException(
            status_code=400,
            detail="Approved quantity must be greater than zero"
        )

    if quantity_approved > purchase_request.requested_quantity:
        raise HTTPException(
            status_code=400,
            detail="Approved quantity cannot exceed requested quantity"
        )

    if quality_grade not in ["A", "B", "C"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid quality grade"
        )

    existing = db.query(QualityInspection).filter(
        QualityInspection.purchase_request_id == request_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Quality inspection already exists"
        )

    inspection = QualityInspection(
        purchase_request_id=request_id,
        inspected_by=farmer.user_id,
        quality_grade=quality_grade,
        quantity_approved=quantity_approved,
        remarks=remarks,
        status="PASSED",
        inspected_at=datetime.utcnow()
    )

    db.add(inspection)

    # Move request to buyer confirmation
    purchase_request.status = "QUALITY_CHECKED"

    db.commit()
    db.refresh(inspection)

    return {
        "message": "Quality inspection completed",
        "inspection_id": inspection.id,
        "quality_grade": inspection.quality_grade,
        "quantity_approved": inspection.quantity_approved,
        "status": inspection.status,
        "next_step": "Buyer confirmation"
    }