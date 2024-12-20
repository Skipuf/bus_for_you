from django.conf import settings
from django.http import HttpResponseRedirect
from dj_rest_auth.registration.views import SocialLoginView, RegisterView, LoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
)

from project.utils import StandardResponseMixin
from .serializers import *
from database.models import *


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CustomRegisterClientView(StandardResponseMixin, RegisterView):
    serializer_class = CustomRegisterClientSerializer

    @swagger_auto_schema(
        tags=["[auth] клиент"],
        operation_description="Регистрация клиентов.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        CustomUser = serializer.save(request=self.request)
        validation_data = serializer.validated_data.copy()

        validation_data.pop('email', None)
        validation_data.pop('password1', None)
        validation_data.pop('password2', None)

        if validation_data.get('client_type') == 'IND':
            CustomUser.first_name = validation_data.pop('first_name', '')
            CustomUser.last_name = validation_data.pop('last_name', '')
            CustomUser.surname = validation_data.pop('surname', '')

        if validation_data.get('client_type') == 'LEG' and \
                validation_data.get('legal_type') == 'OTH':
            validation_data['legal_type'] = validation_data.pop('custom_type', '')

        validation_data.pop('custom_type', None)

        CustomUser.save()
        Client.objects.create(user=CustomUser, **validation_data)

        tokens = get_tokens_for_user(CustomUser)
        return Response({
            "CustomUser": serializer.validated_data,
            "tokens": tokens
        })


class CustomRegisterCarrierView(StandardResponseMixin, RegisterView):
    serializer_class = CustomRegisterCarrierSerializer

    @swagger_auto_schema(
        tags=["[auth] транспортная компания"],
        operation_description="Регистрация транспортных компаний.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        CustomUser = serializer.save(request=self.request)
        validation_data = serializer.validated_data.copy()

        validation_data.pop('email', None)
        validation_data.pop('password1', None)
        validation_data.pop('password2', None)

        if validation_data.get('carrier_type') == 'OTH' and 'custom_type' in validation_data:
            validation_data['carrier_type'] = validation_data.get('custom_type')

        validation_data.pop('custom_type', None)

        CustomUser.save()
        Carrier.objects.create(user=CustomUser, **validation_data)


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(
        f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/"
    )


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


class CustomVerifyEmailView(VerifyEmailView):
    @swagger_auto_schema(
        tags=["[auth] почта"],
        operation_description="Подтверждение почты",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomResendEmailVerificationView(ResendEmailVerificationView):
    @swagger_auto_schema(
        tags=["[auth] почта"],
        operation_description="Повторная отправка сообщения электронной почты",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    @swagger_auto_schema(
        tags=["[auth] пароль"],
        operation_description="Заявка на изменения пароля пользователю, если он его забыл =)",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    @swagger_auto_schema(
        tags=["[auth] пароль"],
        operation_description="Изменение пароля пользователю, из личного кабинета",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GoogleLogin(StandardResponseMixin, SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/"
    client_class = OAuth2Client

    @swagger_auto_schema(
        tags=["[auth] авторизация через сервисы"],
        operation_description="Логин через Google",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        tags=["[auth] авторизация jwt"],
        operation_description="Получения токена",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=["[auth] авторизация jwt"],
        operation_description="Пере выпуск токена",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenVerifyView(TokenRefreshView):
    @swagger_auto_schema(
        tags=["[auth] авторизация jwt"],
        operation_description="Проверка токена.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProtectedEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Вы успешно авторизованы!"})


class CustomClientDetailView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=["[auth] клиент"],
        operation_description="Получить данные клиента.",
    )
    def get(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return Response({"error": "Client not found for this user."}, status=404)

        serializer = CustomClientSerializer(client)
        return Response(serializer.data)

    # @swagger_auto_schema(
    #     operation_description="Обновление данных клиента",
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'first_name',
    #             openapi.IN_FORM,
    #             description="Имя клиента",
    #             type=openapi.TYPE_STRING
    #         ),
    #         openapi.Parameter(
    #             'last_name',
    #             openapi.IN_FORM,
    #             description="Фамилия клиента",
    #             type=openapi.TYPE_STRING
    #         ),
    #         openapi.Parameter(
    #             'surname',
    #             openapi.IN_FORM,
    #             description="Отчество клиента",
    #             type=openapi.TYPE_STRING
    #         ),
    #         openapi.Parameter(
    #             'photo',
    #             openapi.IN_FORM,
    #             description="Фотография клиента",
    #             type=openapi.TYPE_FILE
    #         ),
    #         openapi.Parameter(
    #             'phone_number',
    #             openapi.IN_FORM,
    #             description="Номер телефона клиета",
    #             type=openapi.TYPE_STRING
    #         ),
    #     ],
    #     responses={200: CustomClientSerializer()}
    # )
    @swagger_auto_schema(
        tags=["[auth] клиент"],
        operation_description="Изменить данные клиента.",
    )
    def post(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return Response({"error": "Client not found for this user."}, status=404)

        serializer = CustomClientSerializer(client, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CustomCarrierDetailView(APIView):

#     def get(self, request, *args, **kwargs):
#         try:
#             client = Carrier.objects.get(user=request.user)
#         except Carrier.DoesNotExist:
#             return Response({"error": "Client not found for this user."}, status=404)

#         serializer = CustomCarrierSerializer(client)
#         return Response(serializer.data)

#     @swagger_auto_schema(request_body=CustomCarrierSerializer)
#     def put(self, request, *args, **kwargs):
#         try:
#             carrier = Carrier.objects.get(user=request.user)
#         except Carrier.DoesNotExist:
#             return Response({"error": "Carrier not found for this user."}, status=404)

#         serializer = CustomCarrierSerializer(carrier, data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CarrierDocsView(APIView):

#     def get(self, request, *args, **kwargs):
#         documents = Docs.objects.filter(id_carrier__user=request.user)
#         serializer = Docs(documents)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(request_body=CarrierDocsSerializer)
#     def post(self, request, *args, **kwargs):
#         serializer = CarrierDocsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
