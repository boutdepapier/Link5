from django.contrib.auth.models import User
from twangoo.models import UserProfile
class LoginAsUser:

    def authenticate(self, profile_id=None):
        try:
            user = UserProfile.objects.get(pk=profile_id).user
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id=None):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


