from rest_framework import permissions


class HasRole(permissions.BasePermission):
    message = "You do not have permission to perform this action"
    required_roles = []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.user_roles.filter(role__name__in=self.required_roles).exists()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

# class IsDRO(HasRole):
#    required_roles = 'DRO'


class IsFRO(HasRole):
    message = "You do not have permission to perform this action"
    required_roles = []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_fro


class IsCO(HasRole):
    message = "You do not have permission to perform this action"
    required_roles = []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_co


class IsDRO(permissions.BasePermission):
    message = "You do not have permission to perform this action"
    required_roles = []

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_dro
    

class IsCourseLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get['course_pk']
        return request.user.courses.filter(id=course_id)
