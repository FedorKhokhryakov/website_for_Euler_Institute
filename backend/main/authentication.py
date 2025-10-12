from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .models import ImpersonationSession


class ImpersonationJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            user = User.objects.get(id=user_id)

            if validated_token.get('is_impersonating', False):
                impersonator_id = validated_token.get('impersonator_id')
                if impersonator_id:
                    active_session = ImpersonationSession.objects.filter(
                        target_user=user,
                        impersonator_id=impersonator_id,
                        is_active=True
                    ).first()

                    if not active_session:
                        raise AuthenticationFailed('Сессия имперсонализации неактивна')

            return user
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')