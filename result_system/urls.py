from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views

# Main router for the result system
router = DefaultRouter()
router.register(r"auth/mfa", views.MFAViewSet, basename="mfa")
router.register("courses", views.CourseViewSet, basename="course")
router.register(
    "submitted-results", views.ViewResultViewSet, basename="submitted-result"
)
router.register("ca_max", views.CASlotMaxViewSet, basename="ca-max")

course_router = NestedDefaultRouter(router, "courses", lookup="course")
course_router.register("results", views.ResultViewSet, basename="course-result")

result_router = NestedDefaultRouter(course_router, "results", lookup="result")
result_router.register(
    "assessments", views.AssessmentViewSet, basename="result-assessment"
)

submitted_result = NestedDefaultRouter(router, "submitted-results", lookup="result")
submitted_result.register(
    "scores", views.AssessmentViewSet, basename="submitted-result-score"
)

urlpatterns = [
    # Override Djoser's token create endpoint
    path("auth/token/login/", views.MFATokenCreateView.as_view(), name="login"),
    # Include MFA ViewSet routes
    path("", include(router.urls)),
    # Include other Djoser URLs
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
] + (router.urls + course_router.urls + result_router.urls + submitted_result.urls)
