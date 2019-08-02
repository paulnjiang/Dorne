from django import forms
from user.auth_access import access_auth
from user.models import User


class LoginUserForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        required=True,
        error_messages={'required': '邮箱不能为空'},
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': '公司邮箱'
            }
        )
    )
    password = forms.CharField(
        label="密码",
        required=True,
        error_messages={'required': '密码不能为空'},
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                "placeholder": "密码"
            }
        )
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginUserForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        username = email.strip().split("@")[0]
        # Access认证
        user = access_auth.authenticate(username, password)
        # 判断返回的用户是否为空 并且 用户的邮箱是否跟输入的邮箱匹配
        # 判断邮箱的情况是因为可能用户输入邮箱@前的部分正确 但是@后面部分错误 比如 wangjunjie@miaozh.ccom 这种形式
        # 但是密码正确 也会返回不为空的user 但是此时不应该通过认证
        if user and user.email == email:
            self.user_cache = user
            return self.cleaned_data
        # Access认证返回None的时候 直接去数据库查询是否有该用户的记录
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('用户名或密码不正确')
        # 数据库中没有存储密码 不使用密码的情况下调用check_password肯定返回False
        if user.check_password(password):
            self.user_cache = user
        else:
            raise forms.ValidationError('密码不正确')
        if not self.user_cache.is_active:
            raise forms.ValidationError('账号已被禁用，请联系管理员')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class MyChoiceFiled(forms.ChoiceField):
    def valid_value(self, value):
        return True

class UserInfoForm(forms.Form):
    name = forms.CharField(
        label='用户名',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '用户名',
                'value': "",
                'required': "required",
                'disabled': 'true'
        })
    )
    chinese_name = forms.CharField(
        label='名字',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '名字',
                'value': "",
                'required': "required",
                'disabled': 'true'
        })
    )
    email = forms.EmailField(
        label="邮箱",
        required=True,
        error_messages={'required': "邮箱不能为空"},
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                "placeholder": "公司邮箱",
                'disabled': 'true'
            }
        )
    )

class TeamInfoForm(forms.Form):
    name = forms.CharField(
        label="名字",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '团队名字',
                "value": "",
                "required": "required"
            }
        )
    )

    description = forms.CharField(
        label='描述',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': '描述'
            }
        )
    )

    organization = MyChoiceFiled(
        widget=forms.Select(
            attrs={
                'class': 'selectpicker'
            }
        )
    )

class PermissionForm(forms.Form):
    resource_type = MyChoiceFiled(
        choices=[
            (10, 'System'),
            (20, 'Organization'),
            (30, 'Inventory'),
            (40, 'Project'),
            (50, 'Job Template')
        ]
    )
    object = forms.IntegerField()

    role = MyChoiceFiled()
