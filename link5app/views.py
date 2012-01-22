import urllib, urllib2, oembed

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib import messages

from django.utils.translation import ugettext as _

from link5app.models import Link, Like, Author, Comment, Follow
from link5app.forms import LinkForm, AuthForm, RegisterForm, CommentForm


from django.shortcuts import render_to_response, redirect, get_object_or_404

def home(request, page = 0, user_id = False, author = False, follow = False):
    form = LinkForm() # An unbound form
    
    links = Link.objects.all().order_by('-created_at').select_related()
    if user_id:
        links = links.filter(author__exact = user_id)
        author = Author.objects.get(user=request.user.pk)
        follow = Follow.objects.filter(author_from=request.user.pk).filter(author_to=user_id)
        
    links = links[int(page)*settings.LINK_PER_PAGE:(int(page)+1)*settings.LINK_PER_PAGE+1]
    
    links.page = page
    
    links.home_page = False if int(page) <= 0 else True
    links.last_page = False if len(links) < settings.LINK_PER_PAGE else True
    
    return render_to_response('link5/home.html', {'form': form, 'links': links, 'user_id': user_id, 'author': author, 'follow': follow}, context_instance=RequestContext(request))
   
def link(request):
    if request.method == 'POST': # If the form has been submitted...
        form = LinkForm(request.POST) # A form bound to the POST data
        
        if form.is_valid():
            form.save(request.user)
            messages.info(request,_("Thank you for posting!"))
            return HttpResponseRedirect('/')
    
    else:
        form = LinkForm() # An unbound form
    
    return home(request)

def linkpreview(request, link_id):
    link = Link.objects.get(pk=link_id)
    like = Like.objects.filter(link__exact=link_id).count()
    comments = Comment.objects.filter(link__exact=link_id).order_by("created_at").select_related()
    
    form = CommentForm()
    
    return render_to_response('link5/link_view.html', {'link': link, 'comments': comments, 'form': form}, context_instance=RequestContext(request))

def vote(request, link_id=0, vote=False):
    if not request.user.is_authenticated():
        message = _("You need to login or to register first...")
    else:
        current_link = Link.objects.get(pk=link_id)
        current_author = Author.objects.get(user=request.user.pk)
        like = Like.objects.filter(link__exact=link_id, author__exact=request.user.pk)
        
        if not like:
            #To get track of votes we keep all the vote as single data
            like = Like(link=current_link, author=current_author, point=int(vote))
            like.save()
            message = _("Thank you!")
            #To avoid load we also save the vote total in Link model
            if int(vote)==True:
                current_link.positive += 1
                current_link.save()
            else:
                current_link.negative += 1
                current_link.save()
        else:
            message = _("One vote per Link")
            
    return render_to_response('link5/link_vote.html', {"message": message, "link": current_link}, context_instance=RequestContext(request))
    
def follow(request, user_id = False, status = False):
    if not request.user.is_authenticated():
        message = _("You need to login or to register first...")
    else:    
        au_to = Author.objects.get(user=user_id)
        au_from = Author.objects.get(user=request.user.pk)
        if au_from and au_to:
            follow = Follow.objects.filter(author_from=au_from.pk).filter(author_to=au_to.pk)
            if not follow and int(status) == 1:
                follow = Follow.objects.create(author_from=au_from, author_to=au_to)
                follow.save()
                messages.info(request, _("You now have %s in your follow list" % (au_to.user.username)))
            elif int(status) == 0 and follow:
                follow.delete()
                messages.info(request, _("You have stop following %s" % (au_to.user.username)))
    
    return home(request)
    
def login(request):
    next_url = request.REQUEST.get('next','/') #next value sometimes is passed by GET param
    
    if request.user.is_authenticated():
        if next_url:
            return HttpResponseRedirect(next_url)
        else:
            messages.info(request,_('You have already logged in sneacky avocado :)'))
            return HttpResponseRedirect(reverse("home"))
    
    if request.method == 'POST':
        
        if request.POST.get('register_form') == '1':
            register_form = RegisterForm(request.POST)

            if register_form.is_valid():
                messages.info(request,_('Welcome friend!'))
                register_form.save()
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password1'])
                auth.login(request, user)
                return HttpResponseRedirect(next_url)
        else:
            register_form = RegisterForm()
        
        if 'login_form' in request.POST and request.POST.get('login_form') == '1':
            login_form = AuthForm(request.POST)
            if login_form.is_valid():
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                if user:
                    auth.login(request, user)
                    messages.success(request,_("You're in friend."))
                    return HttpResponseRedirect(next_url)
                else:
                    messages.info(request,_('Haha! wrong password and/or login :p'))
        else:
            login_form = AuthForm()
    
    else:
        login_form = AuthForm()
        register_form = RegisterForm()
    
    return render_to_response('link5/form_login.html', {'login_form': login_form, 'register_form': register_form, 'next': next_url,}, context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    
def profiledit(request):
    return render_to_response('link5/profil_edit.html', {}, context_instance=RequestContext(request))
    
def commentsave(request, link_id=0):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save(request.user, link_id)
            messages.info(request,_("Thank you for your comment!"))
    else:
        form = CommentForm()
        
    return home(request)

# Logo info:
# [col=3399cc]Link[/col][col=115599]5[/col][col=fc0082].me[/col]
# http://creatr.cc/creatr/

def getcontent(request):
    params = {'url': request.GET.get("url", None) , 'key': settings.OEMBED['key'], 'format': settings.OEMBED['format'], 'maxwidth': settings.OEMBED['maxwidth'] }
    oembed_call = "%s%s" % (settings.OEMBED['api_url'], urllib.urlencode(params))
    
    #return HttpResponse(urllib2.urlopen(oembed_call).read(), mimetype='text')
    
    ressoure = oembed.site.embed(request.GET.get("url", None))
    return HttpResponse(ressoure.get_data(), mimetype='text')