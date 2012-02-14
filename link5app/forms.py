import urllib, urllib2

from django.conf import settings

from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site

from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.utils.http import int_to_base36

from django.template import Context, loader

from django.core import serializers

from link5app.models import Link, Category, Author, Comment
import link5app.views

class LinkForm(forms.Form):
    
    post_ttl = forms.CharField(max_length=155)
    post_txt = forms.CharField(widget=forms.Textarea, max_length=255, required=False)
    post_url = forms.URLField(max_length=2000)
    
    categorys = Category.objects.all()
    category = forms.ModelChoiceField(widget=forms.Select(), queryset=categorys, initial=4)
    
    def save(self, user_url = ""):
        link = Link()
        
        link.post_ttl = self.cleaned_data['post_ttl'].encode("utf-8")
        link.post_txt = self.cleaned_data['post_txt']
        link.post_url = self.cleaned_data['post_url']
        link.category = self.cleaned_data['category']
        link.status = "publish"
        
        data = simplejson.loads( link5app.views.getcontent(None, url = self.cleaned_data['post_url']))
        
        link.link_type = data['type']
        if data['type'] == "video" or data['type'] == "rich":
            link.post_html = data['html']
            link.post_img = data['thumbnail_url']
        
        if data['type'] == "link":
            link.post_img = user_url
        
        elif data['type'] == "photo": link.post_img = data['url']
            
        return link
        
class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, max_length=1000, required=True)
    
    def save(self, author, link):
        comment = Comment()
        comment.text = self.cleaned_data['text']
        comment.status = "publish"
        comment.author_id = author.pk
        comment.link_id = link.pk
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
        self.fields['avatar'] = forms.ImageField(required=False)
        self.fields['email'] = forms.EmailField(required=True, max_length=150)
        self.fields['conditions'] = forms.BooleanField(required=True, initial=False)
        
    def save(self, commit=True):
        user = super(auth_forms.UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        author = Author()
        author.newsletter = self.cleaned_data["newsletter"]
        author.conditions = self.cleaned_data["conditions"]
        author.avatar = self.cleaned_data["avatar"]
        author.user = user
        author.save();
        
        return user
        
class UserProfileFrom(forms.ModelForm):
    password1  = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required = False)
    password2  = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required = False)
    
    class Meta:
        model = Author
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(UserProfileFrom, self).__init__(*args, **kwargs)
        self.fields['email']  = forms.EmailField(required=True, max_length=150, initial=self.instance.user.email)
        self.fields['avatar'] = forms.ImageField()
        
    def save(self):
        author = super(UserProfileFrom, self).save(self)
        if self.cleaned_data.get('password1'):
            author.user.set_password(self.cleaned_data["password1"])
        author.user.save()
        author.save()
        
    def clean(self, *args, **kwargs):
        super(UserProfileFrom, self).clean(*args,**kwargs)

        if self.cleaned_data.get('password1') and (self.cleaned_data.get('password1') != self.cleaned_data.get('password2')):
            raise forms.ValidationError(_("Passwords don't match."))
            
        return self.cleaned_data
    
class PasswordResetForm(auth_forms.PasswordResetForm):

    def save(
        self, domain_override=None,
        email_template_name='', use_https=False,
        token_generator=default_token_generator, from_email=None, request=None
    ):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from django.core.mail import EmailMultiAlternatives
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            text_t = loader.get_template('emails/password_reset_email.txt')
            html_t = loader.get_template('emails/password_reset_email.html')
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            msg = EmailMultiAlternatives(
                _("Change of password on %s") % site_name,
                text_t.render(Context(c)), settings.USER_MESSAGE_FROM, [user.email]
            )
            msg.attach_alternative(html_t.render(Context(c)), "text/html")
            msg.send()

        
class ContactForm(forms.Form):
    name    = forms.CharField(max_length=100)
    email   = forms.EmailField()
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)