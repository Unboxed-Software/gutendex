"""
Custom middleware for authorization token-based access control.
"""

from django.conf import settings
from django.http import HttpResponseForbidden
import os


class AuthTokenMiddleware:
    """
    Middleware that restricts access based on authorization token.
    Only allows access when the Authorization header contains the correct Bearer token.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Load the required token from environment variable
        self.required_token = os.getenv('AUTH_TOKEN')
        
    def __call__(self, request):
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        # Check if token validation is enabled and configured
        if self.required_token and not self.is_token_valid(auth_header):
            return HttpResponseForbidden(
                "<h1>Access Denied</h1><p>Invalid or missing authorization token.</p>",
                content_type="text/html"
            )
        
        response = self.get_response(request)
        return response

    def is_token_valid(self, auth_header):
        """
        Check if the authorization header contains the correct Bearer token.
        """
        if not auth_header or not self.required_token:
            return False
            
        # Check if header starts with "Bearer "
        if not auth_header.startswith('Bearer '):
            return False
            
        # Extract the token part
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Compare with required token
        return token == self.required_token 