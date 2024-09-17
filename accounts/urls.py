from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.UserRegistrationViews.as_view(),name='register'),
    path('login/', views.UserLoginViews.as_view(),name='login'),
    path('logout/', views.UserLogoutView.as_view(),name='logout'),
    path('profile/',views.UserBankAccountUpdateView.as_view(), name='profile' ),
    path('porders/pass_change/', views.PassChangeView.as_view(), name='pass_change'),
]
