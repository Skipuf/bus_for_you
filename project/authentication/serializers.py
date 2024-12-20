from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_writable_nested import WritableNestedModelSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from database.models import Client, CustomUser, Carrier, Transport, ExtraService, Route, CLIENT_TYPE, LEGAL_TYPE, Docs, DOC_TYPE


User = get_user_model()


class CustomRegisterClientSerializer(RegisterSerializer):
    client_type = serializers.ChoiceField(choices=CLIENT_TYPE, required=True)
    legal_type = serializers.ChoiceField(choices=LEGAL_TYPE, required=False, allow_null=True)
    custom_type = serializers.CharField(required=False, allow_blank=True) 
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    surname = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    inn = serializers.CharField(required=False, allow_blank=True)
    kpp = serializers.CharField(required=False, allow_blank=True)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    class Meta:
        model = Client
        fields = "__all__"
        
    def validate(self, attrs):
        client_type = attrs.get('client_type')

        if client_type == 'IND':
            self.validate_individual(attrs)
        elif client_type == 'LEG':
            self.validate_legal_entity(attrs)

        return attrs

    def validate_individual(self, attrs):
        required_fields = ['first_name', 'last_name', 'surname', 'phone_number']
        missing_fields = [field for field in required_fields if not attrs.get(field)]

        if missing_fields:
            raise serializers.ValidationError({field: f"This field is required for individuals." for field in missing_fields})

        if attrs.get('legal_type') is not None:
            raise serializers.ValidationError({"legal_type": "Legal type must be empty for individual clients."})

    def validate_legal_entity(self, attrs):
        legal_type = attrs.get('legal_type')
        required_fields = ['company_name', 'inn', 'kpp', 'legal_type']
        missing_fields = [field for field in required_fields if not attrs.get(field)]

        if missing_fields:
            raise serializers.ValidationError({field: f"This field is required for a legal entity." for field in missing_fields})

        if len(attrs.get('kpp', '')) != 9:
            raise serializers.ValidationError({"kpp": "KPP must be 9 characters long."})

        if legal_type is None:
            raise serializers.ValidationError({"legal_type": "This field is required for a legal entity."})

        if legal_type == 'OTH' and not attrs.get('custom_type'):
            raise serializers.ValidationError({"custom_type": "Custom type must be provided when 'Other' is selected."})

        if legal_type == 'IE':
            if len(attrs.get('inn', '')) != 12:
                raise serializers.ValidationError({"inn": "INN must be 12 characters long."})
        else:
            if len(attrs.get('inn', '')) != 10:
                raise serializers.ValidationError({"inn": "INN must be 10 characters long for all other types."})


class CustomRegisterCarrierSerializer(RegisterSerializer):
    carrier_type = serializers.ChoiceField(choices=LEGAL_TYPE, required=True)
    custom_type = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=True)
    inn = serializers.CharField(required=True)
    kpp = serializers.CharField(required=True)

    class Meta():
        model = Carrier
        fields = "__all__"
        
    def validate(self, attrs):
        carrier_type = attrs.get('carrier_type')
        
        if carrier_type is None:
            raise serializers.ValidationError({"carrier_type": "This field is required for a carrier."})
        
        if carrier_type == 'OTH' and not attrs.get('custom_type'):
            raise serializers.ValidationError({"custom_type": "Custom type must be provided when 'Other' is selected."})
            
        if carrier_type == 'IE':
            if len(attrs.get('inn', '')) != 12:  
                raise serializers.ValidationError({"inn": "INN must be 12 characters long."})
        else:
            if len(attrs.get('inn', '')) != 10:  
                raise serializers.ValidationError({"inn": "INN must be 10 characters long."})
            
        if len(attrs.get('kpp', '')) != 9:
            raise serializers.ValidationError({"kpp": "KPP must be 9 characters long."})
        
        return attrs
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'email': self.user.email})
        return data
    
    
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'surname', 'photo']
        read_only_fields = ['email']

    def validate_photo(self, value):
        if value and not value.name.lower().endswith(('jpg', 'jpeg', 'png')):
            raise serializers.ValidationError("Only jpg, jpeg, and png files are allowed.")
        return value

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.surname = validated_data.get('surname', instance.surname)

        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo

        instance.save()
        return instance


def validate_common_fields(attrs, field_prefix):
    ogrn = attrs.get(f'{field_prefix}_ogrn')
    if ogrn and len(ogrn) != 13:
        raise serializers.ValidationError({f'{field_prefix}_ogrn': "OGRN must be 13 characters long."})

    current_account = attrs.get(f'{field_prefix}_current_account')
    if current_account and len(current_account) != 20:
        raise serializers.ValidationError({f'{field_prefix}_current_account': "Current account must be 20 characters long."})

    bik = attrs.get(f'{field_prefix}_bik')
    if bik and len(bik) != 9:
        raise serializers.ValidationError({f'{field_prefix}_bik': "BIK must be 9 characters long."})

    oktmo = attrs.get(f'{field_prefix}_oktmo')
    if oktmo and len(oktmo) not in [8, 11]:
        raise serializers.ValidationError({f'{field_prefix}_oktmo': "OKTMO must be 8 or 11 characters long."})

    corresp_account = attrs.get(f'{field_prefix}_corresp_account')
    if corresp_account:
        if len(corresp_account) != 20 or not corresp_account.startswith('30101') or (bik and corresp_account[-3:] != bik[-3:]):
            raise serializers.ValidationError({
                f'{field_prefix}_corresp_account': "Correspondent account must be 20 characters long, start with 30101, and last 3 digits must match BIK."
            })

    return attrs


class CustomClientSerializer(WritableNestedModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ['id', 'client_type', 'legal_type']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.client_type == 'IND':
            fields_to_remove = [
                'legal_type', 'company_name', 'inn', 'kpp', 'ogrn',
                'current_account', 'corresp_account', 'bik', 'oktmo',
                'legal_address'
            ]
            for field in fields_to_remove:
                representation.pop(field, None)

        return representation

    def validate(self, attrs):
        client_type = attrs.get('client_type')
        legal_type = attrs.get('legal_type')

        if client_type == 'LEG':
            attrs = validate_common_fields(attrs, 'client')

            client_inn = attrs.get('client_inn')
            if legal_type == 'IE' and client_inn and len(client_inn) != 12:
                raise serializers.ValidationError({"client_inn": "INN must be 12 characters long."})
            elif client_inn and len(client_inn) != 10:
                raise serializers.ValidationError({"client_inn": "INN must be 10 characters long."})

            client_kpp = attrs.get('client_kpp')
            if client_kpp and len(client_kpp) != 9:
                raise serializers.ValidationError({"client_kpp": "KPP must be 9 characters long."})

        return attrs

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        instance = super().update(instance, validated_data)

        if user_data:
            user_serializer = self.fields['user']
            user_serializer.update(instance.user, user_data)

        return instance


# class CustomCarrierSerializer(WritableNestedModelSerializer):
#     user = CustomUserSerializer()
    
#     class Meta:
#         model = Carrier
#         fields = "__all__"
#         read_only_fields = ['id', 'carrier_type', 'id_transport', 'id_extra_service', 'id_route'] 
        

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         fields_to_remove = ['id_transport', 'id_extra_service', 'id_route']
        
#         for field in fields_to_remove:
#             representation.pop(field, None)

#         return representation
    
#     def validate(self, attrs):
#         attrs = validate_common_fields(attrs, 'carrier')
        
#         carrier_type = attrs.get('carrier_type')

#         if carrier_type == 'IE':
#             if len(attrs['carrier_inn']) != 12:  
#                 raise serializers.ValidationError({"carrier_inn": "INN must be 12 characters long."})
#         else:
#             if len(attrs['carrier_inn']) != 10:  
#                 raise serializers.ValidationError({"carrier_inn": "INN must be 10 characters long."})

#         if len(attrs['carrier_kpp']) != 9:
#             raise serializers.ValidationError({"carrier_kpp": "KPP must be 9 characters long."})
        
#         return attrs
    
    
#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user', None)
        
#         if user_data:
#             user_serializer = self.fields['user'] 
#             user_serializer.update(instance.user, user_data)
        
#         return instance



# class CarrierDocsSerializer(serializers.ModelSerializer):
#     doc_type = serializers.ChoiceField(choices=DOC_TYPE, required=True)
#     document = serializers.FileField(required=True)

#     class Meta():
#         model = Docs
#         fields =['doc_type', 'document']
#         read_only_fields = ['id_carrier', 'validation']
        
#     def validate(self, attrs):
#         allowed_types = ['pdf', 'doc', 'docx']
        
#         if not attrs.name.split('.')[-1].lower() in allowed_types:
#             raise serializers.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        
#         return attrs