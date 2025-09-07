from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class LoginIdBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their login_id
    instead of username.
    """
    
    def authenticate(self, request, login_id=None, password=None, **kwargs):
        """
        Authenticate user using login_id and password
        """
        if login_id is None or password is None:
            return None
        
        try:
            # Try to find user by login_id
            user = User.objects.get(
                Q(login_id=login_id) | Q(email=login_id),  # Allow login with email as well
                is_active=True
            )
            
            # Check password
            if user.check_password(password):
                return user
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts for 30 minutes
                if user.failed_login_attempts >= 5:
                    from django.utils import timezone
                    user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
                
                user.save(update_fields=['failed_login_attempts', 'locked_until'])
                return None
                
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
