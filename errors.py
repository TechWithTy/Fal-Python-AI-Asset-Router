class FalError(Exception):
    """Base exception for Fal AI SDK"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class FalValidationError(FalError):
    """400: Input validation errors"""
    pass

class FalAuthenticationError(FalError):
    """401: Invalid API key"""
    pass

class FalInsufficientCreditsError(FalError):
    """402: Payment required / Insufficient credits"""
    pass

class FalPermissionError(FalError):
    """403: Permission denied"""
    pass

class FalNotFoundError(FalError):
    """404: Resource not found"""
    pass

class FalRateLimitError(FalError):
    """429: Too many requests"""
    pass

class FalServerError(FalError):
    """500: Internal server error"""
    pass

class FalBadGatewayError(FalError):
    """502: Bad gateway"""
    pass

VALIDATION_ERRORS = {
    400: FalValidationError,
    401: FalAuthenticationError,
    402: FalInsufficientCreditsError,
    403: FalPermissionError,
    404: FalNotFoundError,
    429: FalRateLimitError,
    500: FalServerError,
    502: FalBadGatewayError,
}

def raise_for_status(status_code, text, response=None):
    if status_code in VALIDATION_ERRORS:
        raise VALIDATION_ERRORS[status_code](message=text, status_code=status_code, response=response)
    if status_code >= 400:
        raise FalError(message=f"HTTP {status_code}: {text}", status_code=status_code, response=response)
