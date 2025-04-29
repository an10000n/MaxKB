# coding=utf-8
import datetime
import json
from django.db.models import QuerySet

from users.models.user import User,to_dynamics_permission
from users.models.user_api_key_model import UserApiKeyModel, get_user_dynamics_permission_with_admin_resource
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Permission, Group, Operate, RoleConstants, Auth, get_permission_list_by_role
from common.exception.app_exception import AppAuthenticationFailed
from common.encoder.encoder import SystemEncoder
from django.utils.translation import gettext_lazy as _
from django.core import cache

token_cache = cache.caches['token_cache']


class UserApiKeyAuth(AuthBaseHandle):
    def handle(self, request, token: str, get_token_details):
        code_cache_key = "user-api-key-" + token
        try:
            user = None
            permissions = []

            if(token.endswith("-refresh")):
                token = token.replace("-refresh", "")
                code_cache_key = "user-api-key-" + token
                token_cache.delete(code_cache_key)
            else:
                print("UserApiKeyAuth: get from cache", code_cache_key)
                cache_data = token_cache.get(code_cache_key)
                if(cache_data is not None):
                    auth_json = json.loads(cache_data)
                    user = User(**auth_json.get('user'))
                    permissions = auth_json.get('permissions')
            
            if user is None:
                print("UserApiKeyAuth: get from db", code_cache_key)
                user_api_key = QuerySet(UserApiKeyModel).filter(secret_key=token).first()
                if user_api_key is None:
                    raise AppAuthenticationFailed(500, _('User Api key is invalid'))
                if not user_api_key.is_active:
                    raise AppAuthenticationFailed(500, _('User Api key is invalid'))
                
                user = user_api_key.user
                # 获取用户的应用和知识库的权限
                permissions = get_user_dynamics_permission_with_admin_resource(str(user.id))
        
                from users.serializers.user_serializers import UserInstanceSerializer
                cache_data = {"user" : UserInstanceSerializer(user).data, "permissions" : permissions}
                token_cache.set(code_cache_key, json.dumps(cache_data, cls = SystemEncoder), timeout=datetime.timedelta(minutes = 30))

            rule = RoleConstants[user.role]
            permission_list = get_permission_list_by_role(rule)
            if permissions is not None:
                for permission in permissions:
                    permission_list += to_dynamics_permission(permission.get('type'), permission.get('operate'),
                                                    str(permission.get('id')))
            
            res = (user, Auth(role_list=[rule],
                            permission_list=permission_list,
                            client_id=str(user.id),
                            client_type=AuthenticationType.USER.value,
                            current_role=rule))
            return res
        except Exception as e:
            print(e)
            return (None, Auth([],[]))

    def support(self, request, token: str, get_token_details):
        return str(token).startswith("user-")
