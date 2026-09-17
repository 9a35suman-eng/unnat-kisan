import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from database import get_db
from models import User, Farmer, Customer, BulkBuyer
from schemas import (
    FarmerRegister,
    CustomerRegister,
    LoginRequest
)
from auth import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# =========================
# FARMER REGISTRATION
# =========================

@router.post("/register/farmer")
def register_farmer(
    data: FarmerRegister,
    db: Session = Depends(get_db)
):

    existing_email = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_mobile = db.query(User).filter(
        User.mobile == data.mobile
    ).first()

    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    user = User(
        full_name=data.full_name,
        mobile=data.mobile,
        email=data.email,
        password_hash=hash_password(data.password),
        role="farmer",
        state=data.state,
        district=data.district,
        city_village=data.city_village
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    farmer = Farmer(
        user_id=user.id,
        date_of_birth=data.date_of_birth,
        farm_area=data.farm_area,
        farm_area_unit=data.farm_area_unit
    )

    db.add(farmer)
    db.commit()

    return {
        "message": "Farmer registered successfully",
        "user_id": user.id,
        "role": "farmer"
    }


# =========================
# CUSTOMER REGISTRATION
# =========================

@router.post("/register/customer")
def register_customer(
    data: CustomerRegister,
    db: Session = Depends(get_db)
):

    if data.customer_type not in ["individual", "bulk"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid customer type"
        )

    existing_email = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_mobile = db.query(User).filter(
        User.mobile == data.mobile
    ).first()

    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    user = User(
        full_name=data.full_name,
        mobile=data.mobile,
        email=data.email,
        password_hash=hash_password(data.password),
        role="customer",
        state=data.state,
        district=data.district,
        city_village=data.city_village
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    customer = Customer(
        user_id=user.id,
        customer_type=data.customer_type,
        delivery_address=data.delivery_address
    )

    db.add(customer)
    db.commit()

    return {
        "message": "Customer registered successfully",
        "user_id": user.id,
        "role": "customer",
        "customer_type": data.customer_type
    }


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
        "message": "Login successful",
        "user_id": user.id,
        "full_name": user.full_name,
        "role": user.role,
        "access_token": access_token,
        "token_type": "bearer"
    }

# =========================
# BULK BUYER REGISTRATION
# =========================

@router.post("/register/bulk-buyer")
async def register_bulk_buyer(
    business_name: str = Form(...),
    contact_person: str = Form(...),
    mobile: str = Form(...),
    email: str = Form(...),
    business_type: str = Form(...),
    product_category: str = Form(...),
    monthly_requirement: float = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    city_village: str = Form(...),
    license_number: str = Form(...),
    password: str = Form(...),
    license_photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------
    # 1. Check duplicate email
    # -----------------------------------

    existing_email = db.query(User).filter(
        User.email == email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # -----------------------------------
    # 2. Check duplicate mobile
    # -----------------------------------

    existing_mobile = db.query(User).filter(
        User.mobile == mobile
    ).first()

    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    # -----------------------------------
    # 3. Validate license photo
    # -----------------------------------

    if not license_photo.content_type:
        raise HTTPException(
            status_code=400,
            detail="Invalid license file"
        )

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/webp"
    ]

    if license_photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed"
        )

    # -----------------------------------
    # 4. Create upload directory
    # -----------------------------------

    upload_dir = "upload/licenses"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    # -----------------------------------
    # 5. Generate unique filename
    # -----------------------------------

    extension = os.path.splitext(
        license_photo.filename
    )[1]

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        upload_dir,
        filename
    )

    # -----------------------------------
    # 6. Save license photo
    # -----------------------------------

    file_content = await license_photo.read()

    with open(file_path, "wb") as file:
        file.write(file_content)

    # -----------------------------------
    # 7. Create User
    # -----------------------------------

    user = User(
        full_name=contact_person,
        mobile=mobile,
        email=email,
        password_hash=hash_password(password),
        role="bulk_buyer",
        state=state,
        district=district,
        city_village=city_village
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # -----------------------------------
    # 8. Create Bulk Buyer profile
    # -----------------------------------

    buyer = BulkBuyer(
        user_id=user.id,
        business_name=business_name,
        contact_person=contact_person,
        business_type=business_type,
        product_category=product_category,
        monthly_requirement=monthly_requirement,
        license_number=license_number,
        license_photo=file_path,
        verification_status="PENDING"
    )

    db.add(buyer)
    db.commit()
    db.refresh(buyer)

    # -----------------------------------
    # 9. Response
    # -----------------------------------

    return {
        "message": "Bulk Buyer registration submitted successfully",
        "user_id": user.id,
        "bulk_buyer_id": buyer.id,
        "role": "bulk_buyer",
        "verification_status": buyer.verification_status,
        "license_photo": f"/upload/licenses/{filename}"
    }
