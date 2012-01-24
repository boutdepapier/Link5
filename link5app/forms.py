import urllib, urllib2

from django.conf import settings

from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import forms as auth_forms

from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

from django.core import serializers

from link5app.models import Link, Category, Author, Comment
import link5app.views

class LinkForm(forms.Form):
    
    post_ttl = forms.CharField(max_length=155)
    post_txt = forms.CharField(widget=forms.Textarea, max_length=255, required=False)
    post_url = forms.URLField(max_length=2000)
    
    categorys = Category.objects.all()
    category = forms.ModelChoiceField(widget=forms.Select(), queryset=categorys, initial=4)
    
    def save(self, user, url):
        userprofile = User.objects.get(username=user)
        link = Link()
        
        link.post_ttl = self.cleaned_data['post_ttl']
        link.post_txt = self.cleaned_data['post_txt']
        link.post_url = self.cleaned_data['post_url']
        link.category = self.cleaned_data['category']
        link.status = "publish"
        link.author_id = userprofile.pk
        
        print str(link5app.views.getcontent(None, "http://%s/extracting/?url=%s" % (url, self.cleaned_data['post_url'])))
        data = simplejson.loads(link5app.views.getcontent(None, "http://%s/extracting/?url=%s" % (url, self.cleaned_data['post_url'])))
        
        link.link_type = data['type']
        if data['type'] == "video" or data['type'] == "rich":
            link.post_html = data['html']
            link.post_img = data['thumbnail_url']
        
        elif data['type'] == "photo": link.post_img = data['url']
        
        link.save()
        
class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, max_length=1000, required=True)
    
    def save(self, user, link_id):
        userprofile = User.objects.get(username=user)
        comment = Comment()
        comment.text = self.cleaned_data['text']
        comment.status = "publish"
        comment.author_id = userprofile.pk
        comment.link_id = link_id
        comment.save()
        
class AuthForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(auth_forms.AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'] = forms.CharField(label=_("Email"), max_length=75, required=True)
    
    def clean(self, *args, **kwargs):
        super(auth_forms.AuthenticationForm,self).clean(*args,**kwargs)

        if not (self.cleaned_data.get('username') and self.cleaned_data.get('password')):
            raise forms.ValidationError(_("Please enter username and password."))

        return self.cleaned_data
        
class RegisterForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(auth_forms.UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['newsletter'] = forms.BooleanField(required=False, initial=True)
        self.fields['email'] = forms.EmailField(required=True, max_length=150)
        
    def save(self, commit=True):
        user = super(auth_forms.UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        author = Author()
        author.newsletter = self.cleaned_data["newsletter"]
        author.user = user
        author.save();
        
        return user