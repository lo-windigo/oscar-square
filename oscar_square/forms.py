from django import forms


class SquareNonceForm(forms.Form):
    """
    A form used to submit the Square payment details, and return the nonce value
    """
    nonce = forms.CharField(max_length=300, widget=forms.HiddenInput)

