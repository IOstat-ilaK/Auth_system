from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # профиль urls
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
    
    path('roles/', views.RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('elements/', views.BusinessElementListView.as_view(), name='element-list'),
    path('elements/<int:pk>/', views.BusinessElementDetailView.as_view(), name='element-detail'),
    path('access-rules/', views.AccessRuleListView.as_view(), name='access-rule-list'),
    path('access-rules/<int:pk>/', views.AccessRuleDetailView.as_view(), name='access-rule-detail'),
    # марMOCK url'ы
    path('mock/users/', views.MockUsersView.as_view(), name='mock-users'),
    path('mock/products/', views.MockProductsView.as_view(), name='mock-products'),
    path('mock/orders/', views.MockOrdersView.as_view(), name='mock-orders'),
]