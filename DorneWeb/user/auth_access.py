from user.models import User
from django.conf import settings
import requests, json


class AccessBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            login_result = self.__passport_token(username, password)
            if login_result.get('status'):
                access_token = login_result.get('access_token')
                token_info_result = self.__passport_token_info(access_token)
                if token_info_result.get('status'):
                    username_id = token_info_result.get('username_id')
                    user_info_result = self.__passport_user_info(access_token, username_id)
                    if user_info_result.get('status'):
                        user_data = user_info_result.get('data')
                        try:
                            user = User.objects.get(access_user_id=str(user_data.get('id')))
                        # 用户不存在时 在数据库中新建用户
                        except User.DoesNotExist:
                            try:
                                email = user_data.get('email')
                                user = User(
                                    email=email,
                                    name=email.strip().split('@')[0].replace('.', '_'),
                                    chinese_name=user_data.get('fullname'),
                                    access_user_id=str(user_data.get('id')),
                                    phone=user_data.get('telephone', '')
                                )
                                user.save()
                            except Exception:
                                return None
                        return user
                    else:
                        raise ValueError(user_info_result.get("msg"))
                else:
                    raise ValueError(token_info_result.get("msg"))
            else:
                raise ValueError(login_result.get("msg"))
        except Exception:
            return None


    def __passport_token(self, username, password):
        if username and password:
            auth_data = {
                'grant_type': 'password',
                'username': username,
                'password': password,
                'client_id': 'ops_platform_api',
                'client_secret': '4d1b3314-27ff-4ae5-be6f-305b6b42ef2b',
                'ip': '111.200.229.2',
                'product_id': 35
            }
            auth_url = settings.ACCESS_AUTH_TOKEN
            login_result = json.loads(requests.post(url=auth_url, data=auth_data).text)
            if login_result.get("code") == 0:
                return {'status': True, 'access_token': login_result['data'].get('access_token')}
            else:
                return {'status': False, 'msg': login_result.get('msg')}
        else:
            return {'status': False, 'msg': 'username or password is None'}

    def __passport_token_info(self, access_token):
        token_info_url = settings.ACCESS_TOKEN_INFO
        token_info_data = {'access_token': access_token}
        token_info_result = json.loads(requests.post(url=token_info_url, data=token_info_data).text)
        if token_info_result.get('code') == 0:
            return {'status': True, 'username_id': token_info_result['data'].get('username')}
        else:
            return {'status': False, 'msg': token_info_result.get('msg')}

    def __passport_user_info(self, access_token, username_id):
        user_info_url = settings.ACCESS_USER_INFO
        user_info_data = {
            'access_token': access_token,
            'username': username_id,
            'status': 1
        }
        user_info_result = json.loads(requests.post(url=user_info_url, data=user_info_data).text)
        if user_info_result.get('code') == 0:
            return {'status': True, 'data': user_info_result.get('data')}
        else:
            return {'status': False, 'msg': user_info_result.get('msg')}

access_auth = AccessBackend()

if __name__ == "__main__":
    a = AccessBackend()
    a.authenticate("liukaiqiang", "Tianlkq0608!")
