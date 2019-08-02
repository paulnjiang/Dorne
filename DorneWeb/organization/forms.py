from django import forms

class OrganizationInfoForm(forms.Form):
    name = forms.CharField(
        label='名字',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '组织名字',
                'value': '',
                'required': 'required'
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
