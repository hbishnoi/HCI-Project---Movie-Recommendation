from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('*', views.home, name='home'),
    path('home', views.home, name='home'),
    path('add', views.add, name='add'),
    path('about', views.about, name='about'),
    path('login', views.login, name='login'),
    # path('loginUser', views.loginUser, name='loginUser'),
    path('logout', views.logout, name='logout'),
    # path('signup', views.signup, name='signup'),
    path('register', views.register, name='register'),
    path('recommend', views.recommend, name='recommend'),
    path('movie', views.movie, name='movie'),
    path('details', views.details, name='details'),
    path('title', views.get_recommendations_content_base, name='title'),
    path('genre', views.build_chart, name='genre')
    # path('<int:id>/', views.employee_form, name='employee_update'),
    # path('delete/<int:id>/', views.employee_delete, name='employee_delete'),
    # path('list/', views.employee_list, name='employee_list')
]