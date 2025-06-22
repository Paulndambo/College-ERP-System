from typing import List, Optional, TypedDict, NotRequired, Union, Literal, Any, Dict


"""Basic validation result"""
class ValidationResult(TypedDict):
    is_valid: bool
    error: Optional[str]


"""Invoice-related types"""
class InvoiceResult(TypedDict):
    student_id: int
    student_name: str
    success: bool
    error: Optional[str]


class InvoiceSummary(TypedDict):
    total_students: int
    successful_invoices: int
    failed_invoices: int
    success_rate: float
    failed_invoice_details: NotRequired[List[InvoiceResult]]


"""Response types for different scenarios"""
class SuccessResponse(TypedDict):
    message: str


class ErrorResponse(TypedDict):
    error: str


class PartialSuccessResponse(TypedDict):
    error: str


class PromotionSuccessResponse(InvoiceSummary):
    message: str


"""Serializer error response (Django REST framework format)"""
SerializerErrors = Dict[str, List[str]]


"""Status codes as literals for better type safety"""
StatusCode = Literal[200, 201, 207, 400, 500]


"""Union types for different response data scenarios"""
IndividualReportingResponseData = Union[SuccessResponse, ErrorResponse, PartialSuccessResponse, SerializerErrors]
CohortPromotionResponseData = Union[PromotionSuccessResponse, ErrorResponse]


"""Service method return types"""
IndividualReportingResponse = tuple[bool, IndividualReportingResponseData, StatusCode]
CohortPromotionResponse = tuple[bool, CohortPromotionResponseData, StatusCode]



class ReportingRequestData(TypedDict, total=False):
    """
    Type for semester reporting request data based on SemesterReporting model.
    Using total=False means all fields are optional by default.
    """
    student: int                    
    semester: Optional[int]        
    cohort: Optional[int]           
    academic_year: Optional[str]    
    reported: Optional[bool]        



RequestData = Dict[str, Any]