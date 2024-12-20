from authentication.views import *
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from allauth.socialaccount.views import signup
from django.urls import path
from django.conf.urls.static import static


urlpatterns = [
    path("register/client", CustomRegisterClientView.as_view(), name="rest_register_client"),
    path("register/carrier", CustomRegisterCarrierView.as_view(), name="rest_register_carrier"),
    path("register/verify-email/", CustomVerifyEmailView.as_view(), name="rest_verify_email"),
    path("register/resend-email/", CustomResendEmailVerificationView.as_view(), name="rest_resend_email"),
    path("account-confirm-email/<str:key>/", email_confirm_redirect, name="account_confirm_email"),
    path("account-confirm-email/", VerifyEmailView.as_view(), name="account_email_verification_sent"),
    path("password/reset/", CustomPasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path("password/reset/confirm/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("signup/", signup, name="socialaccount_signup"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("user/client/", CustomClientDetailView.as_view(), name="rest_client_details"),
    # path("user/carrier/", CustomCarrierDetailView.as_view(), name="rest_carrier_details"),
    # path("user/carrier/docs", CarrierDocsView.as_view(), name="rest_carrier_docs"),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('protected/', ProtectedEndpoint.as_view(), name='protected'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

