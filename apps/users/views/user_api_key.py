# coding=utf-8
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request
from django.utils.translation import gettext_lazy as _
from django.core import cache

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, ViewPermission, RoleConstants
from common.log.log import log
from common.response import result
from users.serializers.user_serializers import UserManageSerializer, UserInstanceSerializer

token_cache = cache.caches['token_cache']

class UserApiKey(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_("Add user api key"),
                         operation_id=_("Add user api key"),
                         tags=[_("User management")]
                         )
    @has_permissions(ViewPermission(
        [RoleConstants.ADMIN, RoleConstants.USER],
        [PermissionConstants.USER_READ],
        compare=CompareConstants.AND))
    @log(menu='User management', operate='Add user api key',
         get_operation_object=lambda r, k: {'user_id': r.data.get('user_id', None)})
    def post(self, request: Request, user_id: str):
        return result.success(UserManageSerializer().generate_user_api_key(user_id))

    class ClearUserApiKeyCache(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_("Clear user api key cache"),
                            operation_id=_("Clear user api key cache"),
                            tags=[_("User management")]
                            )
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [PermissionConstants.USER_READ],
            compare=CompareConstants.AND))
        @log(menu='User management', operate='Clear user api key cache',
            get_operation_object=lambda r, k: {'name': r.user.username})
        def post(self, request: Request):
            for key in token_cache.cache.iterkeys():
                if key.startswith('default:user-api-key-'):
                    token_cache.cache.delete(key)
            return result.success(None)