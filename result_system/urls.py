from django.urls import path
from . import views

urlpatterns = [
    #result_url_api_endpoints
    path('results/', views.ResultList.as_view()),
    path('results/<int:pk>', views.ResultDetail.as_view()),
    #department_url_api_endpoints
    path('departments/', views.DepartmentList.as_view()),
    path('departments/<int:pk>', views.DepartmentDetail.as_view()),
    #user_url_api_endpoints
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view()),
    #course_url_api_endpoints
    path('courses/', views.CourseList.as_view()),
    path('courses/<int:pk>', views.CourseDetail.as_view()),
]