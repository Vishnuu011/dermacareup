from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ===================== ORGANIZATION SCHEMAS =====================

class OrganizationCreate(BaseModel):
    org_id: Optional[UUID] = None
    name: str
    type: str
    email: EmailStr
    phone: str
    address: str


class OrganizationUpdate(BaseModel):
    org_id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class OrganizationResponse(BaseModel):
    org_id: UUID
    name: str
    type: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




# ===================== USER SCHEMAS =====================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    organization_id: UUID


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    user_id: UUID
    organization_id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    organization: Optional[OrganizationResponse] = None


class RegisterRequest(BaseModel):
    organization: OrganizationCreate
    user: UserCreate

class RegisterResponse(BaseModel):
    organization: OrganizationResponse
    user: UserResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  

        

class AccountMeResponse(BaseModel):
    user: UserResponse
    organization: OrganizationResponse      

class AccountUpdateRequest(BaseModel):
    user: Optional[UserUpdate] = None
    organization: Optional[OrganizationUpdate] = None

class AccountUpdateResponse(BaseModel):
    user: Optional[UserResponse] = None
    organization: Optional[OrganizationResponse] = None        


class PasswordResetRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str


class PasswordResetResponse(BaseModel):
    message: str = "Password reset successfully"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "Password reset email sent successfully"


# ===================== SUBSCRIPTION SCHEMAS =====================

class SubscriptionCreate(BaseModel):
    organization_id: UUID
    plan_name: str
    scan_limit: int
    price: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str


class SubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = None
    scan_limit: Optional[int] = None
    price: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None


class SubscriptionResponse(BaseModel):
    subscription_id: UUID
    organization_id: UUID
    plan_name: str
    scan_limit: int
    price: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ===================== PAYMENT SCHEMAS =====================

class PaymentCreate(BaseModel):
    organization_id: UUID
    subscription_id: UUID
    stripe_payment_id: Optional[str] = None
    amount: int
    currency: str
    payment_status: str


class PaymentUpdate(BaseModel):
    payment_status: Optional[str] = None
    stripe_payment_id: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: UUID
    organization_id: UUID
    subscription_id: UUID
    stripe_payment_id: Optional[str] = None
    amount: int
    currency: str
    payment_status: str
    payment_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ===================== STRIPE PAYMENT SCHEMAS =====================

class CreatePaymentIntentRequest(BaseModel):
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(default="usd", description="Currency code")
    description: str = Field(default="", description="Payment description")
    subscription_id: Optional[UUID] = None


class PaymentIntentResponse(BaseModel):
    success: bool
    client_secret: str
    payment_intent_id: str
    amount: int
    currency: str
    status: str


class StripeSubscriptionRequest(BaseModel):
    price_id: str = Field(..., description="Stripe price ID for the plan")
    plan_name: str
    scan_limit: int


class StripeSubscriptionResponse(BaseModel):
    success: bool
    subscription_id: str
    customer_id: str
    status: str
    current_period_start: int
    current_period_end: int


class UpdatePaymentStatusRequest(BaseModel):
    stripe_payment_id: str
    payment_status: str


class WebhookEventResponse(BaseModel):
    success: bool
    message: str


class PaymentMethodRequest(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str


class PaymentMethodResponse(BaseModel):
    success: bool
    payment_method_id: str
    card_last4: str


# ===================== PATIENT SCHEMAS =====================

class PatientCreate(BaseModel):
    organization_id: UUID
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class PatientResponse(BaseModel):
    patient_id: UUID
    organization_id: UUID
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===================== RECOMMENDATION SCHEMAS =====================

class RecommendationCreate(BaseModel):
    detection_id: UUID
    recommendation_text: str
    medication: Optional[str] = None
    precautions: Optional[str] = None


class RecommendationUpdate(BaseModel):
    recommendation_text: Optional[str] = None
    medication: Optional[str] = None
    precautions: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendation_id: UUID
    detection_id: UUID
    recommendation_text: Optional[str] = None
    medication: Optional[str] = None
    precautions: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ===================== DETECTION SCHEMAS =====================

class DetectionCreate(BaseModel):
    scan_id: UUID
    disease_name: str
    confidence_score: float
    severity: str
    bounding_box: Optional[str] = None


class DetectionUpdate(BaseModel):
    disease_name: Optional[str] = None
    confidence_score: Optional[float] = None
    severity: Optional[str] = None
    bounding_box: Optional[str] = None


class DetectionResponse(BaseModel):
    detection_id: UUID
    scan_id: UUID
    disease_name: Optional[str] = None
    confidence_score: Optional[float] = None
    severity: Optional[str] = None
    bounding_box: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DetectionDetailResponse(DetectionResponse):
    recommendations: List[RecommendationResponse] = Field(default_factory=list)


# ===================== REPORT SCHEMAS =====================

class ReportCreate(BaseModel):
    scan_id: UUID
    patient_id: UUID
    report_url: str
    email_sent: Optional[bool] = False


class ReportUpdate(BaseModel):
    report_url: Optional[str] = None
    email_sent: Optional[bool] = None


class ReportResponse(BaseModel):
    report_id: UUID
    scan_id: UUID
    patient_id: UUID
    report_url: Optional[str] = None
    generated_at: datetime
    email_sent: bool

    model_config = ConfigDict(from_attributes=True)


# ===================== SCAN ANALYSIS SCHEMAS =====================

class ScanAnalysisCreate(BaseModel):
    scan_id: UUID
    summary: str
    analysis_status: Optional[str] = "completed"
    analysis_data: Optional[Dict[str, Any]] = None


class ScanAnalysisUpdate(BaseModel):
    summary: Optional[str] = None
    analysis_status: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None


class ScanAnalysisResponse(BaseModel):
    analysis_id: UUID
    scan_id: UUID
    summary: Optional[str] = None
    analysis_status: str
    analysis_data: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===================== SCAN SCHEMAS =====================

class ScanCreate(BaseModel):
    organization_id: UUID
    patient_id: UUID
    user_id: UUID
    image_url: str
    scan_status: str


class ScanUpdate(BaseModel):
    image_url: Optional[str] = None
    scan_status: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: UUID
    organization_id: UUID
    patient_id: UUID
    user_id: UUID
    image_url: Optional[str] = None
    scan_status: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanDetailResponse(ScanResponse):
    detections: List[DetectionDetailResponse] = Field(default_factory=list)
    report: Optional[ReportResponse] = None
    analysis: Optional[ScanAnalysisResponse] = None
    patient: Optional[PatientResponse] = None
    user: Optional[UserResponse] = None


# ===================== SCAN USAGE SCHEMAS =====================

class ScanUsageCreate(BaseModel):
    organization_id: UUID
    subscription_id: UUID
    scans_used: int
    scans_remaining: int
    month: int
    year: int


class ScanUsageUpdate(BaseModel):
    scans_used: Optional[int] = None
    scans_remaining: Optional[int] = None


class ScanUsageResponse(BaseModel):
    usage_id: UUID
    organization_id: UUID
    subscription_id: UUID
    scans_used: int
    scans_remaining: int
    month: int
    year: int

    model_config = ConfigDict(from_attributes=True)


# ===================== RESPONSE SCHEMAS =====================

class ErrorResponse(BaseModel):
    status_code: int
    message: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[dict] = None