"""
Custom middleware for IP-based access control.
"""

from django.conf import settings
from django.http import HttpResponseForbidden
import ipaddress


class IPWhitelistMiddleware:
    """
    Middleware that restricts access based on client IP addresses.
    Only allows access from IPs in the ALLOWED_IPS setting.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Load allowed IPs from settings
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        self.allowed_networks = []



        # Parse IP addresses and networks
        for ip in self.allowed_ips:
            try:
                # Try to parse as network (supports CIDR notation)
                self.allowed_networks.append(ipaddress.ip_network(ip, strict=False))
            except ValueError:
                # If it fails, try as individual IP
                try:
                    self.allowed_networks.append(ipaddress.ip_network(f"{ip}/32", strict=False))
                except ValueError:
                    print(f"Warning: Invalid IP address or network: {ip}")

    def __call__(self, request):
        # Get client IP address
        client_ip = self.get_client_ip(request)

        if settings.DEBUG:
            print("IPWhitelistMiddleware =================================================")
            print(f"Allowed IPs: {self.allowed_ips}")
            print(f"Client IP: {client_ip}")
            print(f"Is allowed: {self.is_ip_allowed(client_ip)}")
            print("========================================================================")
        
        # Check if IP whitelist is enabled and configured
        if self.allowed_ips and not self.is_ip_allowed(client_ip):
            return HttpResponseForbidden(
                "<h1>Access Denied</h1><p>Your IP address is not authorized to access this resource.</p>",
                content_type="text/html"
            )
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        Extract the client IP address from the request.
        Handles cases where the app is behind a reverse proxy.
        """
        # Check for forwarded IP (common in production behind reverse proxy)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain (original client)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Direct connection
            ip = request.META.get('REMOTE_ADDR')
        
        return ip

    def is_ip_allowed(self, client_ip):
        """
        Check if the client IP is in the allowed networks.
        """
        if not client_ip:
            return False
            
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            # Check if client IP is in any of the allowed networks
            for network in self.allowed_networks:
                if client_ip_obj in network:
                    return True
                    
        except ValueError:
            # Invalid IP address
            return False
            
        return False 