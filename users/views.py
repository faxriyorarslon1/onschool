from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, Paginator
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_rest_resetpassword.signals import reset_password_token_created
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (CustomTokenObtainPairSerializer, ProfileUpdateSerializer, UpdateSerializer,
                          UserSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()




class UserList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_paginated(self, queryset, page):

        self.paginator = Paginator(queryset, 5)
        try:
            return self.paginator.page(page)
        except EmptyPage:
            return self.paginator.page(self.paginator.num_pages)

    def get(self, request, format=None):

        if request.user.groups.filter(name='dekanat').exists():
            users = User.objects.all().order_by('id')
            paginated_files = self.get_paginated(
                users, request.GET.get('page', 1))
            serializer = UserSerializer(paginated_files, many=True)
            data = {
                'total_users': self.paginator.count,
                'max_per_page': self.paginator.per_page,
                'page_range': [i for i in self.paginator.page_range],
                'results': serializer.data
            }
            return Response(data)
        else:
            return Response(
                {"detail": _(
                    "You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )


class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Page not found.")},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, format=None):
        try:
            user = self.get_object(request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except:
            return Response(
                {"detail": _("User not found.")},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, format=None):
        try:
            user = self.get_object(request.user.id)
            serializer = ProfileUpdateSerializer(
                user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(
                {"detail": _("User not found.")},
                status=status.HTTP_404_NOT_FOUND
            )


class UserChangePass(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Page not found.")},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, format=None):
        try:
            user = self.get_object(request.user.id)
            serializer = UpdateSerializer(
                user, data=request.data, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(
                {"detail": _("Page not found.")},
                status=status.HTTP_404_NOT_FOUND
            )


class UsersRegisterView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if 'password' in request.data:
            if serializer.is_valid():
                password = request.data["password"]
                if len(password) < 8:
                    return Response(
                        {"detail": _(
                            "Password length should not be less than 8 characters.")},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                serializer.save()
                user = User.objects.get(phone=serializer.data['phone'])
                refresh_token = RefreshToken().for_user(user)
                access_token = str(RefreshToken().for_user(user).access_token)
                refresh_token = str(refresh_token.access_token)
                response_data = {'access': access_token,
                                 'refresh': refresh_token}
                response_data.update(serializer.data)
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": _("Password field is required.")},
                status=status.HTTP_400_BAD_REQUEST
            )


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    subject = 'Parolingizni tiklash uchun tasdiqlash kodingiz'
    from_email = 'arslonovfaxriyor@gmail.com'
    to = reset_password_token.user.email

    text_content = f"Sizning tasdiqlash kodingiz:{reset_password_token.key}.Kodni hech kimga bermang"
    html_content = f"Sizning tasdiqlash kodingiz:<strong style='color:blue;'>{reset_password_token.key}</strong>.<hr>Kodni hech kimga bermang"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()