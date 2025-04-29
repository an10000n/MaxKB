# coding=utf-8
from django.core.cache import cache
from django.db.models import QuerySet

from users.models.user_api_key_model import UserApiKeyModel
from common.constants.cache_code_constants import CacheCodeConstants
from common.util.cache_util import get_cache


@get_cache(cache_key=lambda secret_key, use_get_data: secret_key,
           use_get_data=lambda secret_key, use_get_data: use_get_data,
           version=CacheCodeConstants.USER_API_KEY_CACHE.value)
def get_user_api_key(secret_key, use_get_data):
    user_api_key = QuerySet(UserApiKeyModel).filter(secret_key=secret_key).first()
    return {'allow_cross_domain': user_api_key.allow_cross_domain,
            'cross_domain_list': user_api_key.cross_domain_list}


def del_user_api_key(secret_key):
    cache.delete(secret_key, version=CacheCodeConstants.USER_API_KEY_CACHE.value)
