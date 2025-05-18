from django.urls import path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views 

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('students', views.StudentUserViewSet, basename='student')
router.register('lecturers', views.LecturerUserViewSet, basename='lecturer')
router.register('courses', views.CourseViewSet, basename='course')
router.register('results', views.ResultViewSet, basename='result')
router.register('profiles', views.ProfileViewSet)

student_router = NestedDefaultRouter(router, 'students', lookup='students')
student_router.register('results', views.ResultViewSet, basename='users-results')
lecturer_router = NestedDefaultRouter(router, 'lecturers', lookup='lecturer')
lecturer_router.register('courses', views.CourseViewSet, basename='lecturers-courses')

urlpatterns = [
#    #result_url_api_endpoints
#    path('results/', views.ResultList.as_view()),
#    path('results/<int:pk>', views.ResultDetail.as_view()),
#    #department_url_api_endpoints
     #path('departments/<int:pk>', views.DepartmentDetail.as_view()),
     #path('departments/', views.DepartmentListCreateView.as_view()),
#    #user_url_api_endpoints
#    path('users/', views.UserList.as_view()),
#    path('users/<int:pk>', views.UserDetail.as_view()),
#    #course_url_api_endpoints
#    path('courses/', views.CourseList.as_view()),
#    path('courses/<int:pk>', views.CourseDetail.as_view()),
] + router.urls + student_router.urls + lecturer_router.urls