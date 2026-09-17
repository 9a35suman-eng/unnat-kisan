from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    Text,
    DateTime
)

from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    mobile = Column(String(20), unique=True, nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(30), nullable=False)

    state = Column(String(100))

    district = Column(String(100))

    city_village = Column(String(150))

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    date_of_birth = Column(Date)

    farm_area = Column(Float)

    farm_area_unit = Column(String(20), default="acre")


class BulkBuyer(Base):
    __tablename__ = "bulk_buyers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    business_name = Column(String(200), nullable=False)

    contact_person = Column(String(150))

    business_type = Column(String(100))

    product_category = Column(String(100))

    monthly_requirement = Column(Float)

    license_number = Column(
        String(150),
        nullable=False
    )

    license_photo = Column(
        String(500),
        nullable=False
    )

    verification_status = Column(
        String(30),
        default="PENDING"
    )

    rejection_reason = Column(Text)

    verified_by = Column(Integer)

    verified_at = Column(DateTime)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    customer_type = Column(
        String(30),
        nullable=False
    )

    delivery_address = Column(Text)


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(Integer, primary_key=True, index=True)

    buyer_id = Column(Integer, nullable=False)

    product_name = Column(
        String(100),
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False
    )

    quantity_unit = Column(
        String(20),
        default="kg"
    )

    expected_price = Column(Float)

    required_by = Column(Date)

    state = Column(String(100))

    district = Column(String(100))

    city = Column(String(150))

    description = Column(Text)

    status = Column(
        String(30),
        default="OPEN"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
class CropListing(Base):
    __tablename__ = "crop_listings"

    id = Column(Integer, primary_key=True, index=True)

    farmer_id = Column(Integer, nullable=False)

    crop_name = Column(
        String(100),
        nullable=False
    )

    harvest_date = Column(
        Date,
        nullable=False
    )

    quality_grade = Column(
        String(20),
        nullable=False
    )

    quantity = Column(
        Float,
        nullable=False
    )

    quantity_unit = Column(
        String(20),
        default="kg"
    )

    expected_price_per_kg = Column(
        Float,
        nullable=False
    )

    state = Column(
        String(100),
        nullable=False
    )

    district = Column(
        String(100),
        nullable=False
    )

    city = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    photos = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        default="AVAILABLE"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True)

    crop_id = Column(Integer, nullable=False)
    buyer_id = Column(Integer, nullable=False)

    requested_quantity = Column(Float, nullable=False)
    offered_price_per_kg = Column(Float, nullable=False)

    message = Column(Text, nullable=True)

    # PENDING → ACCEPTED / REJECTED
    status = Column(String(30), default="PENDING")

    farmer_response = Column(Text, nullable=True)

    responded_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id = Column(Integer, primary_key=True, index=True)
    purchase_request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)

    inspected_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    quality_grade = Column(String(20), nullable=False)
    quantity_approved = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)

    status = Column(String(30), default="PENDING")
    # PENDING / PASSED / FAILED

    inspected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    purchase_request_id = Column(
        Integer,
        ForeignKey("purchase_requests.id"),
        nullable=False
    )

    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("bulk_buyers.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop_listings.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    quantity_unit = Column(String(30), nullable=False)

    price_per_kg = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    status = Column(String(40), default="QUALITY_PENDING")
    # QUALITY_PENDING
    # BUYER_CONFIRMATION_PENDING
    # PAYMENT_PENDING
    # PAYMENT_PROOF_UPLOADED
    # PAYMENT_VERIFIED
    # COMPLETED

    created_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(String(50), nullable=True)

    payment_proof = Column(String(500), nullable=True)

    status = Column(String(30), default="PENDING")
    # PENDING
    # PROOF_UPLOADED
    # VERIFIED
    # REJECTED

    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)