from fastapi import status
from typing import Optional, Any, Dict


# ===================== BASE EXCEPTION CLASS =====================

class CustomException(Exception):
    """Base custom exception class"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        detail: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.detail = detail
        super().__init__(self.message)


# ===================== AUTHENTICATION EXCEPTIONS =====================

class AuthenticationException(CustomException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
            detail=detail
        )


class InvalidCredentialsException(CustomException):
    """Raised when credentials are invalid"""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(CustomException):
    """Raised when token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenException(CustomException):
    """Raised when token is invalid"""
    def __init__(self, message: str = "Invalid or malformed token"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN"
        )


class UserNotExistException(CustomException):
    """Raised when user does not exist"""
    def __init__(self, message: str = "User does not exist"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="USER_NOT_EXIST"
        )


# ===================== AUTHORIZATION EXCEPTIONS =====================

class AuthorizationException(CustomException):
    """Raised when user is not authorized to perform action"""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_FAILED"
        )


class InsufficientPermissionsException(CustomException):
    """Raised when user has insufficient permissions"""
    def __init__(self, message: str = "Insufficient permissions", required_role: Optional[str] = None):
        detail = f"Required role: {required_role}" if required_role else None
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PERMISSIONS",
            detail=detail
        )


class AccessDeniedException(CustomException):
    """Raised when access is denied"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCESS_DENIED"
        )


class CloudinaryUploadException(CustomException):
    """Raised when Cloudinary upload fails"""
    def __init__(self, message: str = "Failed to upload image to Cloudinary", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="CLOUDINARY_UPLOAD_FAILED",
            detail=detail
        )

class AgentException(CustomException):
    def __init__(self, message: str = "Failed to generate recomentation", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="AGENT_RECOMMENDATION_FAIL",
            detail=detail
        )     

class AIPipelineException(CustomException):
    def __init__(self, message: str = "Failed to AI Pipeline", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="AI_PIPELINE_FAIL",
            detail=detail
        )           

# ===================== RESOURCE NOT FOUND EXCEPTIONS =====================

class ResourceNotFoundException(CustomException):
    """Raised when resource is not found"""
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id: {resource_id}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=f"{resource.upper()}_NOT_FOUND"
        )


class UserNotFoundException(ResourceNotFoundException):
    """Raised when user is not found"""
    def __init__(self, user_id: Optional[str] = None):
        super().__init__("User", user_id)


class OrganizationNotFoundException(ResourceNotFoundException):
    """Raised when organization is not found"""
    def __init__(self, org_id: Optional[str] = None):
        super().__init__("Organization", org_id)


class PatientNotFoundException(ResourceNotFoundException):
    """Raised when patient is not found"""
    def __init__(self, patient_id: Optional[str] = None):
        super().__init__("Patient", patient_id)


class ScanNotFoundException(ResourceNotFoundException):
    """Raised when scan is not found"""
    def __init__(self, scan_id: Optional[str] = None):
        super().__init__("Scan", scan_id)


class DetectionNotFoundException(ResourceNotFoundException):
    """Raised when detection is not found"""
    def __init__(self, detection_id: Optional[str] = None):
        super().__init__("Detection", detection_id)


class SubscriptionNotFoundException(ResourceNotFoundException):
    """Raised when subscription is not found"""
    def __init__(self, subscription_id: Optional[str] = None):
        super().__init__("Subscription", subscription_id)


class PaymentNotFoundException(ResourceNotFoundException):
    """Raised when payment is not found"""
    def __init__(self, payment_id: Optional[str] = None):
        super().__init__("Payment", payment_id)


class ReportNotFoundException(ResourceNotFoundException):
    """Raised when report is not found"""
    def __init__(self, report_id: Optional[str] = None):
        super().__init__("Report", report_id)


class RecommendationNotFoundException(ResourceNotFoundException):
    """Raised when recommendation is not found"""
    def __init__(self, recommendation_id: Optional[str] = None):
        super().__init__("Recommendation", recommendation_id)


# ===================== VALIDATION EXCEPTIONS =====================

class ValidationException(CustomException):
    """Raised when validation fails"""
    def __init__(self, message: str = "Validation failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            detail=detail
        )


class InvalidEmailException(ValidationException):
    """Raised when email is invalid"""
    def __init__(self, email: str):
        super().__init__(message=f"Invalid email format: {email}")


class DuplicateEmailException(ValidationException):
    """Raised when email already exists"""
    def __init__(self, email: str):
        super().__init__(message=f"Email already registered: {email}")


class InvalidPasswordException(ValidationException):
    """Raised when password is invalid"""
    def __init__(self, message: str = "Password does not meet requirements"):
        super().__init__(message=message)


class InvalidPhoneException(ValidationException):
    """Raised when phone is invalid"""
    def __init__(self, phone: str):
        super().__init__(message=f"Invalid phone format: {phone}")


class MissingRequiredFieldException(ValidationException):
    """Raised when required field is missing"""
    def __init__(self, field_name: str):
        super().__init__(message=f"Required field missing: {field_name}")


class InvalidAgeException(ValidationException):
    """Raised when age is invalid"""
    def __init__(self, age: int):
        super().__init__(message=f"Invalid age: {age}. Age must be between 0 and 150")


# ===================== DATABASE EXCEPTIONS =====================

class DatabaseException(CustomException):
    """Raised when database operation fails"""
    def __init__(self, message: str = "Database operation failed", detail: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            detail=detail
        )


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message=message)


class DatabaseIntegrityException(DatabaseException):
    """Raised when database integrity constraint is violated"""
    def __init__(self, message: str = "Database integrity constraint violated"):
        super().__init__(message=message)


class DuplicateRecordException(DatabaseException):
    """Raised when attempting to create a duplicate record"""
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(
            message=f"Duplicate {entity}: {field} '{value}' already exists"
        )


# ===================== SUBSCRIPTION & PAYMENT EXCEPTIONS =====================

class SubscriptionException(CustomException):
    """Raised when subscription operation fails"""
    def __init__(self, message: str = "Subscription operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="SUBSCRIPTION_ERROR"
        )


class InvalidSubscriptionException(SubscriptionException):
    """Raised when subscription is invalid"""
    def __init__(self, message: str = "Invalid subscription"):
        super().__init__(message=message)


class SubscriptionExpiredException(SubscriptionException):
    """Raised when subscription has expired"""
    def __init__(self, message: str = "Subscription has expired"):
        super().__init__(message=message)


class PaymentException(CustomException):
    """Raised when payment operation fails"""
    def __init__(self, message: str = "Payment operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PAYMENT_ERROR"
        )


class PaymentFailedException(PaymentException):
    """Raised when payment processing fails"""
    def __init__(self, message: str = "Payment processing failed"):
        super().__init__(message=message)


class InvalidPaymentException(PaymentException):
    """Raised when payment details are invalid"""
    def __init__(self, message: str = "Invalid payment details"):
        super().__init__(message=message)


# ===================== SCAN & QUOTA EXCEPTIONS =====================

class ScanException(CustomException):
    """Raised when scan operation fails"""
    def __init__(self, message: str = "Scan operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="SCAN_ERROR"
        )


class ScanQuotaExceededException(ScanException):
    """Raised when scan quota is exceeded"""
    def __init__(self, scans_used: int, scan_limit: int):
        super().__init__(
            message=f"Scan quota exceeded. Used: {scans_used}/{scan_limit}"
        )


class InsufficientQuotaException(ScanException):
    """Raised when there is insufficient quota for operation"""
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient quota. Required: {required}, Available: {available}"
        )


class InvalidScanStatusException(ScanException):
    """Raised when scan status is invalid"""
    def __init__(self, current_status: str, allowed_transitions: list):
        super().__init__(
            message=f"Invalid scan status: {current_status}. Allowed: {', '.join(allowed_transitions)}"
        )


class ScanProcessingException(ScanException):
    """Raised when scan processing fails"""
    def __init__(self, message: str = "Scan processing failed"):
        super().__init__(message=message)


# ===================== FILE UPLOAD EXCEPTIONS =====================

class FileUploadException(CustomException):
    """Raised when file upload fails"""
    def __init__(self, message: str = "File upload failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR"
        )


class InvalidFileTypeException(FileUploadException):
    """Raised when file type is invalid"""
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"Invalid file type: {file_type}. Allowed: {', '.join(allowed_types)}"
        )


class FileSizeExceededException(FileUploadException):
    """Raised when file size exceeds limit"""
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size exceeds limit. Size: {file_size}MB, Max: {max_size}MB"
        )


# ===================== BUSINESS LOGIC EXCEPTIONS =====================

class BusinessLogicException(CustomException):
    """Raised when business logic operation fails"""
    def __init__(self, message: str = "Business logic operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_LOGIC_ERROR"
        )


class OrganizationCreationException(BusinessLogicException):
    """Raised when organization creation fails"""
    def __init__(self, message: str = "Failed to create organization"):
        super().__init__(message=message)


class UserCreationException(BusinessLogicException):
    """Raised when user creation fails"""
    def __init__(self, message: str = "Failed to create user"):
        super().__init__(message=message)


class RoleAssignmentException(BusinessLogicException):
    """Raised when role assignment fails"""
    def __init__(self, message: str = "Failed to assign role"):
        super().__init__(message=message)


class InvalidRoleException(ValidationException):
    """Raised when role is invalid"""
    def __init__(self, role: str, allowed_roles: list):
        super().__init__(
            message=f"Invalid role: {role}. Allowed: {', '.join(allowed_roles)}"
        )


class OperationNotAllowedException(BusinessLogicException):
    """Raised when operation is not allowed"""
    def __init__(self, message: str = "Operation not allowed"):
        super().__init__(message=message)


class InvalidStateTransitionException(BusinessLogicException):
    """Raised when state transition is invalid"""
    def __init__(self, entity: str, current_state: str, requested_state: str):
        super().__init__(
            message=f"Invalid {entity} state transition from {current_state} to {requested_state}"
        )


# ===================== EXTERNAL SERVICE EXCEPTIONS =====================

class ExternalServiceException(CustomException):
    """Raised when external service fails"""
    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(
            message=f"{service}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR"
        )


class StripeException(ExternalServiceException):
    """Raised when Stripe API fails"""
    def __init__(self, message: str = "Stripe payment failed"):
        super().__init__("Stripe", message)


class EmailServiceException(ExternalServiceException):
    """Raised when email service fails"""
    def __init__(self, message: str = "Email sending failed"):
        super().__init__("Email Service", message)


class AIServiceException(ExternalServiceException):
    """Raised when AI service fails"""
    def __init__(self, message: str = "AI detection service failed"):
        super().__init__("AI Service", message)


# ===================== RATE LIMIT EXCEPTIONS =====================

class RateLimitException(CustomException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )


# ===================== CONFIGURATION EXCEPTIONS =====================

class ConfigurationException(CustomException):
    """Raised when configuration is invalid"""
    def __init__(self, message: str = "Configuration error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CONFIGURATION_ERROR"
        )


class MissingConfigException(ConfigurationException):
    """Raised when required configuration is missing"""
    def __init__(self, config_key: str):
        super().__init__(message=f"Missing required configuration: {config_key}")
