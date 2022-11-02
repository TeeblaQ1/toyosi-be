from django.urls import path
from authentication.views import ListAddressesAPIView, LogoutAPIView, PasswordChangeAPIView, RecentItemsAPIView, RequestVerificationLink, SavedItemsAPIView, RegisterView, RequestPasswordResetEmail, SetNewPasswordAPIView, UpdateProfileAPIView, VerifyEmail, LoginView, PasswordTokenCheckAPI
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('request-verification-link/', RequestVerificationLink.as_view(), name="request-verification-link"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email/verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token-refresh"),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),
    path('address/', ListAddressesAPIView.as_view(), name="address-list"),
    path('profile/', UpdateProfileAPIView.as_view(), name="profile-update"),
    path('password-change/', PasswordChangeAPIView.as_view(), name="password-change"),
    path('saved-items/', SavedItemsAPIView.as_view(), name="saved-items"),
    path('recent-items/', RecentItemsAPIView.as_view(), name="recent-items"),
]