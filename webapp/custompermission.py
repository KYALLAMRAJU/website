from rest_framework.permissions import BasePermission, SAFE_METHODS

class mypermission1(BasePermission):

    def has_permission(self, request, view):
        print(request.method)
        print("inside my custom permission class - mypermission1")
        if request.method in SAFE_METHODS:   # SAFE_METHODS are GET, HEAD, OPTIONS
            return True
        else:
            return False