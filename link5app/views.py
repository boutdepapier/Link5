from datetime import datetime, timedelta

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template import Context, loader
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import get_current_site

from django.utils.translation import ugettext as _
from django.utils import simplejson

from link5app.models import Link, Like, Author, Comment, Follow
from link5app.forms import LinkForm, AuthForm, RegisterForm, CommentForm, ContactForm, UserProfileFrom

from django.shortcuts import render_to_response, redirect, get_object_or_404


def home(request, page = 0, user_name = False, author = False, follow = False, referral = False, period = False, url = False, filters = False, category = False, link_id = False):

    if request.method == 'POST' and not referral: # If the form has been submitted...
        form = LinkForm(request.POST) # A form bound to the POST data
        
        if form.is_valid():
            link = form.save(request.POST.get("user_url", None))
            if request.user.is_authenticated():
                author = Author.objects.get(user=request.user.pk)
                link.author = author
                link.save()
                messages.info(request,_("Thank you for posting!"))
                return HttpResponseRedirect('/')
            else:
                request.session['link'] = True
                request.session['url'] = link.post_url
                
                request.session['post_ttl']  = link.post_ttl
                request.session['post_txt']  = link.post_txt
                request.session['post_url']  = link.post_url
                request.session['category']  = link.category
                request.session['link_type'] = link.link_type
                request.session['post_html'] = link.post_html
                request.session['post_img']  = link.post_img
                
                messages.info(request,_("Please login or register to publish your link"))
                return HttpResponseRedirect('/login/')
    
    else:
        form = LinkForm() # An unbound form
    
    if link_id:
        links = Link.objects.all().filter(pk = link_id)
    else:
        links = Link.objects.all().order_by('-created_at').filter(status__exact="publish").select_related()
        if period:
            links = links.filter(created_at__gte=period).extra(select={"score": "positive - negative"}).extra(order_by = ['-score'])
            
        if category:
            links = links.filter(category__slug=category)
            
        if user_name:
            try:
                author = Author.objects.get(user__username__exact=user_name)
                author.number_from = Follow.objects.all().filter(author_to__exact = author.pk).count() - 1
                author.number_to   = Follow.objects.all().filter(author_from__exact = author.pk).count() - 1
                links = links.filter(author__exact = author.pk)
                url = "user"
                
                if request.user.is_authenticated():
                    follow = Follow.objects.filter(author_from=request.user.pk).filter(author_to=author.pk)
            except:
                return HttpResponseRedirect('/')
        
    links = links[int(page)*settings.LINK_PER_PAGE:(int(page)+1)*settings.LINK_PER_PAGE+1]
    
    for link in links:
        link.comment = Comment.objects.filter(link=link.pk).count()
    
    links.page = page
    
    links.home_page = False if int(page) <= 0 else True
    links.last_page = False if len(links) < settings.LINK_PER_PAGE + 1 else True
    
    return render_to_response('link5/home.html', {'form': form, 'links': links, 'user_name': user_name, 'author': author, 'follow': follow, 'url': url, 'LINK_PER_PAGE': ":%s" % settings.LINK_PER_PAGE}, context_instance=RequestContext(request))
    
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
    if request.user.is_authenticated():
        author = get_object_or_404(Author, user=request.user.pk)
        followings = Follow.objects.all().filter(author_from__exact = author.pk)
        links = Link.objects.all().order_by('-created_at').filter(status__in=["publish", "denied"]).select_related().filter(author__in=[following.author_to for following in followings])[int(page)*settings.LINK_PER_PAGE:(int(page)+1)*settings.LINK_PER_PAGE+1]
        form = LinkForm()
        url = "user/links"
        
        links.page = page
        
        links.home_page = False if int(page) <= 0 else True
        links.last_page = False if len(links) < settings.LINK_PER_PAGE + 1 else True
         
        return render_to_response('link5/home.html', {'form': form, 'links': links, 'url': url, 'LINK_PER_PAGE': ":%s" % settings.LINK_PER_PAGE}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')
    
def linkdelete(request, link_id):
    try:
        link = Link.objects.get(pk=link_id)
        author = Author.objects.get(user=request.user.pk)
        if link.author.pk == author.pk:
            link.delete()
            messages.info(request,_('Link deleted master!'))
    except:
        messages.info(request,_('Error, delete failed'))
    
    return home(request)

def linkpreview(request, link_id, refresh = False):
    try:
        link = Link.objects.get(pk=link_id)
        like = Like.objects.filter(link__exact=link_id).count()
        comments = Comment.objects.filter(link__exact=link_id).order_by("created_at").select_related()
        
        form = CommentForm()
        
        if refresh:
            return render_to_response('link5/comments.html', {'link': link, 'comments': comments, 'form': form, }, context_instance=RequestContext(request))
        
        from urlparse import urlparse
        link.source = urlparse(link.post_url)
        
        return render_to_response('link5/link_view.html', {'link': link, 'comments': comments, 'form': form, }, context_instance=RequestContext(request))
    except:
        raise Http404(_("Cannot find link..."))

def vote(request, link_id=0, vote=False):
    current_link = False
    if not request.user.is_authenticated():
        message = _("Please login first")
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
            else:
                current_link.negative += 1
            if current_link.positive - current_link.negative <= settings.MODERATION_LEVEL:
                current_link.status = "denied"
            print current_link.positive + current_link.negative
            current_link.save()
        else:
            message = _("One vote per Link")
            
    return render_to_response('link5/link_vote.html', {"message": message, "link": current_link}, context_instance=RequestContext(request))
    
def follow(request, user_id = False, status = False):
    if not request.user.is_authenticated():
        messages.info(request, _("You need to login or to register first..."))
    else:
        author = Author.objects.get(user=request.user.pk)
        au_to = Author.objects.get(user=user_id)
        au_from = Author.objects.get(user=author.pk)
        if au_from and au_to:
            follow = Follow.objects.filter(author_from=au_from.pk).filter(author_to=au_to.pk)
            if not follow and int(status) == 1:
                number_from = Follow.objects.all().filter(author_from__exact = author.pk).count()
                if number_from + 1 > settings.MAX_FOLLOW:
                    messages.info(request, _("Sorry you can't follow more than %s persons" % (settings.MAX_FOLLOW)))
                else:
                    
                    from django.core.mail import EmailMultiAlternatives
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                        
                    text_t = loader.get_template('emails/new_follower.txt')
                    html_t = loader.get_template('emails/new_follower.html')
                    c = {
                        'email': au_to.user.email,
                        'domain': domain,
                        'site_name': site_name,
                        'author_to': au_to,
                        'author_from': au_from,
                        'protocol': 'http',
                    }
                    msg = EmailMultiAlternatives(
                        _("Congratulation! You have a new link follower on %s!") % site_name,
                        text_t.render(Context(c)), settings.USER_MESSAGE_FROM, [au_to.user.email]
                    )
                    msg.attach_alternative(html_t.render(Context(c)), "text/html")
                    msg.send()
                    
                    follow = Follow.objects.create(author_from=au_from, author_to=au_to)
                    follow.save()
                    messages.info(request, _("You now have %s in your follow list" % (au_to.user.username)))
            elif int(status) == 0 and follow and au_to != au_from:
                follow.delete()
                messages.info(request, _("You have stop following %s" % (au_to.user.username)))
            elif au_to == au_from:
                messages.info(request, _("Can't stop your own music man!"))
    
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
            register_form = RegisterForm(request.POST, request.FILES)

            if register_form.is_valid():
                messages.info(request,_('Welcome friend!'))
                register_form.save()
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password1'])
                auth.login(request, user)
                author = Author.objects.get(user=user.pk)
                follow = Follow.objects.create(author_from=author, author_to=author)
                follow.save()
        else:
            register_form = RegisterForm()
        
        if 'login_form' in request.POST and request.POST.get('login_form') == '1':
            login_form = AuthForm(request.POST)
            if login_form.is_valid():
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
                if user:
                    auth.login(request, user)
                    author = Author.objects.get(user=user.pk)
                    messages.success(request,_("You're in friend."))
                else:
                    messages.info(request,_('Haha! wrong password and/or login :p'))
        else:
            login_form = AuthForm()
            
        # If the new user has a link in Session, time to post it!
        if 'link' in request.session and (login_form.is_valid() or register_form.is_valid()):
            link = Link()
            link.post_url = request.session['url'] 
            link.status   = "publish"
            
            link.post_ttl = request.session['post_ttl']
            link.post_txt = request.session['post_txt']
            link.post_url = request.session['post_url']
            link.category = request.session['category']
            link.link_type = request.session['link_type']
            link.post_html = request.session['post_html']
            link.post_img = request.session['post_img']
            
            link.author = author
            
            link.save()
            
            request.session['link'] = False
            messages.info(request,_("Thank you for posting!"))
            
        if login_form.is_valid() or register_form.is_valid():
            return HttpResponseRedirect(next_url)
    
    else:
        login_form = AuthForm()
        register_form = RegisterForm()
    
    return render_to_response('link5/form_login.html', {'login_form': login_form, 'register_form': register_form, 'next': next_url,}, context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    
def profiledit(request, page_to = 0, page_from = 0, user_name = False):
    try:
        author             = Author.objects.get(user__username__exact=user_name)
        followers          = Follow.objects.all().filter(author_to__exact = author.pk)
        author.number_from = Follow.objects.all().filter(author_to__exact = author.pk).count() - 1
        followings         = Follow.objects.all().filter(author_from__exact = author.pk)
        author.number_to   = Follow.objects.all().filter(author_from__exact = author.pk).count() -1
        edit_form = False
        
        if request.user.is_authenticated() and request.user.pk == author.pk:
            follow    = Follow.objects.filter(author_from=request.user.pk).filter(author_to=author.pk)
            
            if request.method == 'POST':
                edit_form = UserProfileFrom(request.POST, request.FILES, instance = author)
        
                if edit_form.is_valid():
                    messages.info(request,_('Profil updated'))
                    edit_form.save()
            else:
                edit_form = UserProfileFrom(instance = author)
        else:
            follow = False
        
        return render_to_response('link5/profil_edit.html', {'author': author, 'follow': follow, 'followers': followers, 'followings': followings, 'edit_form': edit_form}, context_instance=RequestContext(request))
    except:
        #raise Http404(_("Cannot find profil"))
        #return HttpResponseRedirect('/')
        raise
    
def commentsave(request, link_id=0):
    referral = "commentsave"
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_author = Author.objects.get(user=request.user.pk)
            link = Link.objects.get(pk=link_id)
            link_author = Author.objects.get(user=link.author)
            
            if (comment_author.pk != link_author.pk):
                from django.core.mail import EmailMultiAlternatives
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                    
                text_t = loader.get_template('emails/comment.txt')
                html_t = loader.get_template('emails/comment.html')
                c = {
                    'email': link_author.user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'comment_author': comment_author,
                    'link': link,
                    'link_author': link_author,
                    'text': form.cleaned_data['text'],
                    'protocol': 'http',
                }
                msg = EmailMultiAlternatives(
                    _("New comment waiting for you on %s!") % site_name,
                    text_t.render(Context(c)), settings.USER_MESSAGE_FROM, [link_author.user.email]
                )
                msg.attach_alternative(html_t.render(Context(c)), "text/html")
                msg.send()
        
            form.save(comment_author, link)
            messages.info(request,_("Thank you for your comment!"))
    else:
        form = CommentForm()
        
    return home(request, referral=referral)
    
def commentdelete(request, link_id=0, comment_id=0):
    referral = "commentdelete"
    
    try:
        author = Author.objects.get(user=request.user.pk)
        comment = Comment.objects.get(id=comment_id)
        
        if author.pk == comment.author.pk:
            comment.delete()
            messages.info(request,_("Comment deleted Sir!"))
    except:
        pass
    
    return home(request, referral=referral)

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
            title=''; description=''; image_list = []
            
            try:
                request = urllib2.Request(original_url)
                response = urllib2.urlopen(request)
                html = response.read()     
                       
                try:
                    soup = BeautifulSoup(html, fromEncoding="UTF-8")
                    #soup.encode('utf-8')
                    
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
                        try:
                            title = soup.title.string
                        except:
                            pass
                    
                    try:
                        max_images = settings.MAX_IMAGE
                        image_tags = soup.findAll('img', limit=max_images)
                        image_urls_list = []
                        for image_tag in image_tags:
                            original_url_shem = urlparse(original_url)
                            #If the url is absolute
                            if (urlparse(image_tag.get('src')).scheme):
                                image_urls_list.append(image_tag.get('src'))
                            #else we have to build it
                            else:
                                image_urls_list.append("%s://%s%s" % (original_url_shem.scheme, original_url_shem.netloc, urlparse(image_tag.get('src')).path))
                        
                        for img_url in image_urls_list:
                            file = urllib2.urlopen(img_url)
                            size = file.headers.get("content-length")
                            file.close()
                            if int(size) > settings.MIM_IMAGE_SIZE:
                                image_list.append({'url': img_url})
                    except:
                        pass
                        
                except:
                    title = _("error parsing")
                    description = _("Please send me the url so I can check")
            except:
                title = _("Error URL doesn't answer...")
                description = _("Please retry later on...")
            
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
    
