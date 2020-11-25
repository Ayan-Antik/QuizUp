from django import forms


class PostForm(forms.Form):
    #topic_list = (("1", "Sports"), ("2", "History"))
    post = forms.CharField(widget=forms.Textarea)
    #Topics = forms.MultipleChoiceField( widget=forms.SelectMultiple, required=False)
    #img = forms.ImageField(required=False)


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)