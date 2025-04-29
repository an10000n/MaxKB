# coding=utf-8
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request
from django.utils.translation import gettext_lazy as _

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, ViewPermission, RoleConstants
from common.log.log import log
from common.response import result
from users.serializers.user_serializers import UserManageSerializer, UserInstanceSerializer

class Tenant3DIUser(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Add 3DI tenant user"),
                         operation_id=_("Add 3di tenant user"),
                         request_body=UserManageSerializer.UserInstance.get_request_body_api(),
                         responses=result.get_api_response(UserInstanceSerializer.get_response_body_api()),
                         tags=[_("User management")]
                         )
    @has_permissions(ViewPermission(
        [RoleConstants.ADMIN],
        [PermissionConstants.USER_READ],
        compare=CompareConstants.AND))
    @log(menu='User management', operate='Add 3DI tenant user',
         get_operation_object=lambda r, k: {'name': r.data.get('username', None)})
    def post(self, request: Request):
        return result.success(UserManageSerializer().save_3di_user(request.data))
