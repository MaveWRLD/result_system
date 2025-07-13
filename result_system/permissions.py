from rest_framework import permissions

from result_system.models import Result


class IsResultDraft(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action == "submit":
            return True
        if "status" in request.data:
            current_status = obj.status
            print(current_status)
            new_status = request.data["status"]
            print(new_status)
            if current_status != "D":
                return False
            if new_status != "P_D":
                return False
            return True

    def _is_lecturer(self, user):
        return hasattr(user) and user.is_lecturer


class CanCreateResult(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        course_pk = view.kwargs.get("course_pk")
        if not course_pk:
            return False
        if Result.objects.filter(course_id=course_pk).exists():
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class IsResultAssessmentDraft(permissions.BasePermission):
    message = "Result can not be changed when submitted. Request to DRO for changes"

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True
        if user.is_co:
            return True
        if obj.result.status == "D":
            return True


class ViewResultRoles(permissions.BasePermission):
    message = "You are not authorized to make this status change"

    def has_object_permission(self, request, view, obj):
        # Always allow safe methods (GET, HEAD, OPTIONS)
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow status changes via PATCH/PUT
        if request.method not in ["PATCH", "PUT"]:
            return True

        # Get the requested new status
        new_status = request.data.get("status")
        if not new_status:
            return True  # Not changing status

        # Get user role
        user = request.user
        current_status = obj.status

        # Define allowed transitions for each role
        allowed_transitions = {
            "dro": {"P_D": ["P_F", "D"]},
            "fro": {"P_F": ["A", "P_D"]},
            "co": {},  # CO can't make any status changes
        }

        # Check if user has permission for this transition
        for role, transitions in allowed_transitions.items():
            if getattr(user, f"is_{role}", False):
                if current_status in transitions:
                    return new_status in transitions[current_status]
                return False  # No transitions allowed for current status

        return False  # No matching role found


class RoleBasedStatusChangePermission(permissions.BasePermission):
    """
    Allows status changes only according to role-specific transitions:
    - Lecturers: Can only change from DRAFT (D) to PENDING_DEPARTMENT (P_D)
    - DRO: Can change from P_D to PENDING_FACULTY (P_F) or REJECTED (R)
    - FRO: Can change from P_F to APPROVED (A) or REJECTED (R)
    - CO: Can only view approved results (no status changes)
    """
