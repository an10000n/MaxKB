# coding=utf-8
import os
import uuid

from django.db import models
from django.db.models import QuerySet
from common.db.sql_execute import select_list
from common.util.file_util import get_file_content
from common.constants.permission_constants import RoleConstants
from common.mixins.app_model_mixin import AppModelMixin
from django.contrib.postgres.fields import ArrayField
from users.models.user import User, to_dynamics_permission
from smartdoc.conf import PROJECT_DIR

__all__ = ["UserApiKeyModel", "get_user_dynamics_permission_with_admin_resource"]

def get_user_dynamics_permission_with_admin_resource(user_id: str):
    """
    获取 应用和数据集权限
    :param user_id: 用户id
    :return: 用户 应用和数据集权限
    """
    permission_sql = get_file_content(os.path.join(PROJECT_DIR, "apps", "setting",'sql', 'get_user_permission.sql'))
    member_permission_list = select_list(
        permission_sql,
        [user_id, user_id, user_id])
    admin_user = QuerySet(User).filter(role=RoleConstants.ADMIN.name).first()
    admin_permission_list = select_list(
        permission_sql,
        [str(admin_user.id), str(admin_user.id), str(admin_user.id)])

    return admin_permission_list + member_permission_list
    

class UserApiKeyModel(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    secret_key = models.CharField(max_length=1024, verbose_name="秘钥", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    is_active = models.BooleanField(default=True, verbose_name="是否开启")
    allow_cross_domain = models.BooleanField(default=False, verbose_name="是否允许跨域")
    cross_domain_list = ArrayField(verbose_name="跨域列表",
                                   base_field=models.CharField(max_length=128, blank=True)
                                   , default=list)

    class Meta:
        db_table = "user_api_key"