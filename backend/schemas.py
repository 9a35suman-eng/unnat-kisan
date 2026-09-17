from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


# =========================
# COMMON USER SCHEMA
# =========================

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    mobile: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    state: Optional[str] = None
    district: Optional[str] = None
    city_village: Optional[str] = None


# =========================
# FARMER REGISTRATION
# =========================

class FarmerRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    mobile: str = Field(..., min_length=10, max_length=20)
    email: EmailStr

    date_of_birth: Optional[date] = None

    state: str
    district: str
    city_village: str

    farm_area: Optional[float] = None
    farm_area_unit: str = "acre"

    password: str = Field(..., min_length=8)


# =========================
# CUSTOMER REGISTRATION
# =========================

class CustomerRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    mobile: str = Field(..., min_length=10, max_length=20)
    email: EmailStr

    customer_type: str

    state: str
    district: str
    city_village: str
    delivery_address: str

    password: str = Field(..., min_length=8)


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# API RESPONSE
# =========================

class MessageResponse(BaseModel):
    message: str
    user_id: Optional[int] = None

class BuyerRequirementCreate(BaseModel):

    product_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    quantity: float = Field(
        ...,
        gt=0
    )

    quantity_unit: str = "kg"

    expected_price: Optional[float] = None

    required_by: Optional[date] = None

    state: Optional[str] = None

    district: Optional[str] = None

    city: Optional[str] = None

    description: Optional[str] = None

# =========================
# CROP LISTING
# =========================

class CropListingCreate(BaseModel):

    crop_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    harvest_date: date

    quality_grade: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    quantity: float = Field(
        ...,
        gt=0
    )

    quantity_unit: str = "kg"

    expected_price_per_kg: float = Field(
        ...,
        gt=0
    )

    state: str

    district: str

    city: str

    description: Optional[str] = None

class PurchaseRequestCreate(BaseModel):
    crop_id: int = Field(..., gt=0)
    requested_quantity: float = Field(..., gt=0)
    offered_price_per_kg: float = Field(..., gt=0)
    message: Optional[str] = None