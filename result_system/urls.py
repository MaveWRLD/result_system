#from django.urls import path
#from rest_framework.routers import DefaultRouter
#from . import views
#
#router = DefaultRouter()
#router.register('departments', views.DepartmentViewSet)
#router.register('users', views.UserViewSet)
#router.register('courses', views.CourseViewSet)
#router.register('results', views.ResultViewSet)
#
#urlpatterns = router.urls
#[
#    #result_url_api_endpoints
#    path('results/', views.ResultList.as_view()),
#    path('results/<int:pk>', views.ResultDetail.as_view()),
#    #department_url_api_endpoints
#    path('departments/', views.DepartmentList.as_view()),
#    path('departments/<int:pk>', views.DepartmentDetail.as_view()),
#    #user_url_api_endpoints
#    path('users/', views.UserList.as_view()),
#    path('users/<int:pk>', views.UserDetail.as_view()),
#    #course_url_api_endpoints
#    path('courses/', views.CourseList.as_view()),
#    path('courses/<int:pk>', views.CourseDetail.as_view()),
#]