from datetime import datetime, timedelta

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib import messages

from django.utils.translation import ugettext as _
from django.utils import simplejson

from link5app.models import Link, Like, Author, Comment, Follow
from link5app.forms import LinkForm, AuthForm, RegisterForm, CommentForm, ContactForm

from django.shortcuts import render_to_response, redirect, get_object_or_404


def home(request, page = 0, user_id = False, author = False, follow = False, referral = False, period = False, url = False, filters = False):

    if request.method == 'POST' and not referral: # If the form has been submitted...
        form = LinkForm(request.POST) # A form bound to the POST data
        
        if form.is_valid():
            author = Author.objects.get(user=request.user.pk)
            form.save(author)
            messages.info(request,_("Thank you for posting!"))
            return HttpResponseRedirect('/')
    
    else:
        form = LinkForm() # An unbound form
    
    links = Link.objects.all().order_by('-created_at').select_related()
    if period:
        links = links.filter(created_at__gte=period).order_by('-positive')
        
    if user_id:
        links = links.filter(author__exact = user_id)
        author = Author.objects.get(pk=user_id)
        url = "user"
        if request.user.is_authenticated():
            follow = Follow.objects.filter(author_from=request.user.pk).filter(author_to=user_id)
        
    links = links[int(page)*settings.LINK_PER_PAGE:(int(page)+1)*settings.LINK_PER_PAGE+1]
    
    links.page = page
    
    links.home_page = False if int(page) <= 0 else True
    links.last_page = False if len(links) < settings.LINK_PER_PAGE + 1 else True
    
    return render_to_response('link5/home.html', {'form': form, 'links': links, 'user_id': user_id, 'author': author, 'follow': follow, 'url': url, 'LINK_PER_PAGE': ":%s" % settings.LINK_PER_PAGE}, context_instance=RequestContext(request))
    
def linkday(request, page = 0):
    yesterday = datetime.now() - timedelta(days=1)
    return home (request, period = yesterday, page = page, url = "day") 
    
def linkweek(request, page = 0):
    yesterday = datetime.now() - timedelta(days=7)
    return home (request, period = yesterday, page = page, url = "week") 
    
def linkmonth(request, page = 0):
    yesterday = datetime.now() - timedelta(days=31)
    return home (request, period = yesterday, page = page, url = "month")

def userlinks(request, page = 0):
    author = Author.objects.get(user=request.user.pk)
    followings = Follow.objects.all().filter(author_from__exact = author.pk)
    links = Link.objects.all().order_by('-created_at').select_related().filter(author__in=[following.author_to for following in followings])[int(page)*settings.LINK_PER_PAGE:(int(page)+1)*settings.LINK_PER_PAGE+1]
    form = LinkForm()
    url = "user/links"
    
    links.page = page
    
    links.home_page = False if int(page) <= 0 else True
    links.last_page = False if len(links) < settings.LINK_PER_PAGE + 1 else True
     
    return render_to_response('link5/home.html', {'form': form, 'links': links, 'url': url, 'LINK_PER_PAGE': ":%s" % settings.LINK_PER_PAGE}, context_instance=RequestContext(request))

def linkpreview(request, link_id):
    link = Link.objects.get(pk=link_id)
    like = Like.objects.filter(link__exact=link_id).count()
    comments = Comment.objects.filter(link__exact=link_id).order_by("created_at").select_related()
    
    form = CommentForm()
    
    return render_to_response('link5/link_view.html', {'link': link, 'comments': comments, 'form': form, }, context_instance=RequestContext(request))

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
        messages.info(request, _("You need to login or to register first..."))
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
    followers = Follow.objects.all().filter(author_from__exact = request.user.pk)
    followings = Follow.objects.all().filter(author_from__exact = request.user.pk)
    
    return render_to_response('link5/profil_edit.html', {'followers': followers, 'followings': followings,}, context_instance=RequestContext(request))
    
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

    
#With Oembed module
def getcontent(request, url = False):
    import urllib, urllib2, oembed, re, mimetypes
    from BeautifulSoup import BeautifulSoup
    import simplejson as json
    from urlparse import urlparse

    if url:
        original_url = url
    else:
        original_url = request.GET.get("url", None)
    
    #First shot to analyse link content is for oembed module, more info here: http://oembed.com/
    try:
        oembed_obj = oembed.site.embed(original_url, format=settings.OEMBED['format'], maxwidth=settings.OEMBED['maxwidth'])
        oembed_obj = simplejson.dumps(oembed_obj.get_data())
    #Other URL will have to get manual processing
    except:
        image_types = ('image/bmp', 'image/jpeg', 'image/png', 'image/gif', 'image/tiff', 'image/x-icon')
        # If the link is directly on the image media
        if mimetypes.guess_type(original_url)[0] in image_types:
            oembed_obj = {'type': 'photo', 'url': original_url}
            oembed_obj = json.dumps(oembed_obj)
        else:
            request = urllib2.Request(original_url)
            
            response = urllib2.urlopen(request)
            html = response.read()
            soup = BeautifulSoup(html)
            
            title=''; description=''
            description = soup.findAll('meta', attrs={'name':re.compile("^description$")})
            if description:
               description = description[0].get('content')
            else: 
                try:  
                    description = soup.findAll('meta', attrs={'property':re.compile("description$", re.I)})[0].get('content')
                except:
                    pass

        
            # Try to get the page title from the meta tag named title
            try:
                title = soup.findAll('meta', attrs={'name':re.compile("^title$", re.I)})[0].get('content')
            except:
                pass
        
            # If the meta tag does not exist, grab the title from the title tag.
            if not title:
                title = soup.title.string
            
            max_images = 20
            image_tags = soup.findAll('img', limit=max_images)
            image_urls_list = []
            for image_tag in image_tags:
                original_url_shem = urlparse(original_url)
                image_urls_list.append("%s://%s%s" % (original_url_shem. scheme, original_url_shem.netloc, urlparse(image_tag.get('src')).path))
            
            image_list = []
            for img_url in image_urls_list:
               image_list.append({'url': img_url})
            
            return_dict = {'title':title, 'description':description, 'type': "link", 'url': original_url}
            return_dict.update({'images': image_list})
            
            oembed_obj = json.dumps(return_dict)
    
    if url:
        return oembed_obj
    return HttpResponse(oembed_obj, mimetype='text')
    
def contact(request):
    
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = "Lnk5: %s" % form.cleaned_data['subject']
            message = "Yo Mr. Ours !\n\nVous avez un message qui viens de : %s\nSon contact : %s \n\nSon petit mot dou :\n%s \n\n------------------------------------------\n\nWho's awsome ? Your awsome !\nBiz !\n\n\n" % (name, email, form.cleaned_data['message'])

            from django.core.mail import send_mail
            send_mail(subject, message, settings.CONTACT_FROM, settings.CONTACT_RECIPIENT)
            messages.info(request,_("Thank you for your message!"))
            
            return home(request, referral = True) # Redirect after POST
    
    else:
        form = ContactForm() # An unbound form

    return render_to_response('link5/form_contact.html', { 'form': form,}, context_instance=RequestContext(request))
    
