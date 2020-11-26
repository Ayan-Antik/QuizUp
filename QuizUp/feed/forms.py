from django import forms


class PostForm(forms.Form):

    post = forms.CharField(widget=forms.Textarea)


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
