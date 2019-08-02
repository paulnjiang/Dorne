from django import forms

class MyChoiceFiled(forms.ChoiceField):
    def valid_value(self, value):
        return True

class ProjectInfoForm(forms.Form):
    name = forms.CharField(
        label='名字',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'maxlength': 32,
                'placeholder': '项目名字',
                'value': '',
                'required': 'required'
        })
    )

    description = forms.CharField(
        label='描述',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': '描述',
                'rows': 5
            }
        )
    )

    organization_id = MyChoiceFiled(
        widget=forms.Select(
            attrs={
                'class': 'form-control selectpicker',
            }
        )
    )

    scm_type = forms.ChoiceField(
        choices=[(1, 'Git')],
        widget=forms.Select(
            attrs={
                'class': 'form-control selectpicker'
            }
        )
    )

    url = forms.CharField(
        required=True,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': '远程URL地址',
                'required': 'required'
            }
        )
    )

    branch = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '分支',
                'value': ''
            }
        )
    )
    revision = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Revision'
            }
        )
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '用户名',
                'required': 'required'
            }
        )
    )
