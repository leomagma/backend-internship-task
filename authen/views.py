from rest_framework import generics, permissions,status
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .serializer import UserSerializer, RegisterSerializer , CaloSerializer
from .pagenation import CustomPagination

"""from .env import SECRET_KEY"""


"""Register API"""
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
      try:
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          user = serializer.save()
          return Response({
          "user": UserSerializer(user, context=self.get_serializer_context()).data,
          "token": AuthToken.objects.create(user)[1]
          })
      except:
        return Response("Invalid Details! ")
        
          

"""login API"""
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
      try:
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        while True:
            response = redirect('/project')
            return response
      except:
        err_msg="UNAUTHORIZED ACCESS!,try again with valid credentials"
        return Response({"msg":err_msg})
      


"""crud users"""
class UserManger(APIView):
  permissions_classes = (permissions.AllowAny)
  pagination_class = CustomPagination

  @property
  def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator
  def paginate_queryset(self, queryset):
        
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                   self.request, view=self)
  def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
  
  
  def get(self,requst,*args,**kwargs):
    user = User.objects.all()
    page = self.paginate_queryset(user)
    if page is not None:
            serializer = self.get_paginated_response(UserSerializer(page,many=True).data)
    else:
      serializer = UserSerializer(user, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
 
  def post(self,request,*args,**kwargs):  
      data = {
        'username': request.data.get('username'), 
        'email': request.data.get('email'),
        'password': request.data.get('password'),
    }

      serializer = RegisterSerializer(data=data)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



  def delete(self, request, id, *args, **kwargs):
      if User.objects.filter(id=id).exists():
        project = User.objects.get(id=id)
        project.delete()
        return Response({"response":"User Deleted"}, status=status.HTTP_200_OK)
      else:
          return Response(
              {"res": "User Doesn't Exists"},
              status=status.HTTP_400_BAD_REQUEST
          )
      
  def patch(self, request, id, *args, **kwargs):
    if User.objects.filter(id=id).exists():
      project = User.objects.get(id=id)
      data = {
      "username":request.data.get("username"),
      "email" :request.data.get("email")
      }
      serializer = UserSerializer(instance = project, data=data, partial = True)
      if serializer.is_valid():
          serializer.save()
          return Response(serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(
                {"res": "User Doesn't Exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )