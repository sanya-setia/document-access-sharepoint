#Raised when authentication fails
class GraphAuthError(Exception):
    """Problem during Microsoft Graph authentication."""
    pass


# Raised when Graph API returns a non-OK HTTP status
class GraphHttpError(Exception):
    """Microsoft Graph returned an HTTP error."""
    def __init__(self, status: int, detail: str):
        # Example: "HTTP 404: File not found"
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status
        self.detail = detail
