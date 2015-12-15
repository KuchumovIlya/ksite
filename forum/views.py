from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import django
from .models import Section, Topic, Message, UserData
from .forms import RegistrationForm
from django.shortcuts import render
from django.db.models import Max

import random
import string

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr

import ksite.settings
import requests


def _add_username(request, namespace):
    if request.user.is_authenticated():
        namespace['username'] = request.user.username


def index_view(request):
    sections_list = Section.objects.all()
    template = loader.get_template('forum/index.html')
    namespace = {
        'sections_list': sections_list
    }
    error_message = request.GET.get('error_message')
    if error_message is not None:
        namespace['error_message'] = error_message
    _add_username(request, namespace)
    context = RequestContext(request, namespace)
    return HttpResponse(template.render(context))


def section_view(request, section_id):
    topics_list = Topic.objects.filter(section_id=section_id)
    template = loader.get_template('forum/section.html')
    section = Section.objects.filter(section_id=section_id)[:1].get()
    namespace = {
        'topics_list': topics_list,
        'section_id': section_id,
        'section': section
    }
    error_message = request.GET.get('error_message')
    if error_message is not None:
        namespace['error_message'] = error_message
    _add_username(request, namespace)
    context = RequestContext(request, namespace)
    return HttpResponse(template.render(context))


def topic_view(request, section_id, topic_id):
    message_list = Message.objects.filter(topic_id=topic_id)
    template = loader.get_template('forum/topic.html')
    section = Section.objects.filter(section_id=section_id)[:1].get()
    topic = Topic.objects.filter(topic_id=topic_id)[:1].get()
    namespace = {
        'message_list': message_list,
        'section_id': section_id,
        'topic_id': topic_id,
        'topic': topic,
        'section': section
    }
    error_message = request.GET.get('error_message')
    if error_message is not None:
        namespace['error_message'] = error_message
    _add_username(request, namespace)
    context = RequestContext(request, namespace)
    return HttpResponse(template.render(context))


def add_section_view(request):
    if request.user.is_authenticated() and request.user.username == 'admin':
        section_name = request.POST['section_name']
        section_id = Section.objects.all().aggregate(Max('section_id'))['section_id__max']
        section_id = section_id + 1 if section_id is not None else 1
        section = Section()
        section.section_name = section_name
        section.section_id = section_id
        section.save()
        return HttpResponseRedirect(reverse('forum:index'))
    return HttpResponse('Access denied.')


def add_topic_view(request, section_id):
    if request.user.is_authenticated():
        topic_name = request.POST['topic_name']
        topic_id = Topic.objects.all().aggregate(Max('topic_id'))['topic_id__max']
        topic_id = topic_id + 1 if topic_id is not None else 1
        topic = Topic()
        topic.topic_name = topic_name
        topic.topic_id = topic_id
        topic.section_id = section_id
        topic.modification_date = django.utils.timezone.now()
        topic.save()
        return HttpResponseRedirect(reverse('forum:section', kwargs={'section_id': section_id}))
    return HttpResponse('Access denied.')


def submit_message_view(request, section_id, topic_id):
    if request.user.is_authenticated():
        text = request.POST['message_text']
        message_id = Message.objects.all().aggregate(Max('message_id'))['message_id__max']
        message_id = message_id + 1 if message_id is not None else 1
        message = Message()
        message.message_text = text
        message.publication_date = django.utils.timezone.now()
        message.topic_id = topic_id
        message.user_name = request.user.username
        message.message_id = message_id
        message.save()

        topic = Topic.objects.filter(topic_id=topic_id)[:1].get()
        topic.modification_date = django.utils.timezone.now()
        topic.save()

        return HttpResponseRedirect(reverse('forum:topic', kwargs={'section_id': section_id, 'topic_id': topic_id}))
    return HttpResponse('Access denied.')


def authentication_view(request):
    template = loader.get_template('forum/authentication.html')
    namespace = dict()
    error_message = request.GET.get('error_message')
    if error_message is not None:
        namespace['error_message'] = error_message
    context = RequestContext(request, namespace)
    return HttpResponse(template.render(context))


def authorization_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if username != 'admin':
            user_data = UserData.objects.filter(username=username)[:1].get()
            if not user_data.is_confirmed:
                _send_confirming_token(username)
                url = reverse('forum:authentication')
                url += '?' + 'error_message=Confirm your email.'
                return HttpResponseRedirect(url)
        login(request, user)
        return HttpResponseRedirect(reverse('forum:index'))
    else:
        url = reverse('forum:authentication')
        url += '?' + 'error_message=invalid login or password'
        return HttpResponseRedirect(url)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('forum:index'))


def registration_view(request):
    namespace = dict()
    error_message = request.GET.get('error_message')
    if error_message is not None:
        namespace['error_message'] = error_message
    reg_form = RegistrationForm()
    namespace['form'] = reg_form
    context = RequestContext(request, namespace)
    return render(request, 'forum/registration.html', context)


def _gen_rand_token(length=10):
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


def _get_user_data(username):
    return UserData.objects.filter(username=username)[:1].get()


def _regen_confirming_token(username):
    user_data = _get_user_data(username)
    user_data.confirming_token = _gen_rand_token()
    user_data.save()
    return user_data.confirming_token


def _send_confirming_token(username):
    token = _regen_confirming_token(username)
    email = User.objects.filter(username=username)[:1].get().email

    mime = MIMEMultipart()
    mime['From'] = 'ksitesender@yandex.ru'
    mime['To'] = email
    mime['Subject'] = 'access token'
    url = 'http://ilya.kolambda.com/' + reverse('forum:confirm')
    url += '?token={}&username={}'.format(token, username)
    message = 'To confirm your email click here: {}'.format(url)
    mime.attach(MIMEText(message))

    mail_server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    mail_server.ehlo()
    mail_server.login('ksitesender@yandex.ru', 'kuchumov')
    mail_server.sendmail('ksitesender@yandex.ru', email, mime.as_string())
    mail_server.quit()


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _grecaptcha_verify(request):
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': ksite.settings.NORECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': _get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)


def registration_authorization_view(request):
    error_url = reverse('forum:registration') + '?' + 'error_message={}.'

    if not _grecaptcha_verify(request):
        return HttpResponseRedirect(error_url.format('Invalid captcha'))

    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']

    if username == '':
        return HttpResponseRedirect(error_url.format('Username needed'))

    if parseaddr(email) == ('', ''):
        return HttpResponseRedirect(error_url.format('Incorrect email'))

    if User.objects.filter(username=username).exists():
        return HttpResponseRedirect(error_url.format('There is such user'))

    user = User.objects.create_user(username, email, password)
    user.save()

    user_data = UserData()
    user_data.username = username
    user_data.confirming_token = _gen_rand_token()
    user_data.is_confirmed = False
    user_data.save()
    _send_confirming_token(username)

    return HttpResponseRedirect(error_url.format('Successful registration. Confirm your email'))


def confirm_view(request):
    token = request.GET.get('token')
    username = request.GET.get('username')
    user_data = _get_user_data(username)
    right_token = user_data.confirming_token
    if token == right_token:
        user_data.is_confirmed = True
        user_data.save()
        url = reverse('forum:authentication')
        url += '?' + 'error_message=Email is confirmed. You can login now.'
        return HttpResponseRedirect(url)
    return HttpResponseRedirect(reverse('forum:index'))


def user_list_view(request):
    user_list = User.objects.all()
    template = loader.get_template('forum/user_list.html')
    namespace = {
        'user_list': user_list
    }
    _add_username(request, namespace)
    context = RequestContext(request, namespace)
    return HttpResponse(template.render(context))


def delete_user_view(request, username):
    if not request.user.is_authenticated() or (request.user.username != 'admin' and request.user.username != username):
        return HttpResponse('Access denied.')
    if username == 'admin':
        return HttpResponse('Can not delete admin')

    for message in Message.objects.filter(user_name=username):
        topic = Topic.objects.filter(topic_id=message.topic_id)[:1].get()
        topic.modification_date = django.utils.timezone.now()
        topic.save()

    User.objects.filter(username=username).delete()
    Message.objects.filter(user_name=username).delete()
    UserData.objects.filter(username=username).delete()

    return HttpResponseRedirect(reverse('forum:user_list'))


def delete_section_view(request, section_id):
    if not request.user.is_authenticated() or request.user.username != 'admin':
        return HttpResponse('Access denied.')

    Message.objects.filter(topic_id__in=Topic.objects.filter(section_id=section_id)).delete()
    Topic.objects.filter(section_id=section_id).delete()
    Section.objects.filter(section_id=section_id).delete()

    return HttpResponseRedirect(reverse('forum:index'))


def delete_topic_view(request, section_id, topic_id):
    if not request.user.is_authenticated() or request.user.username != 'admin':
        return HttpResponse('Access denied.')

    Message.objects.filter(topic_id=topic_id).delete()
    Topic.objects.filter(topic_id=topic_id).delete()

    return HttpResponseRedirect(reverse('forum:section', kwargs={'section_id': section_id}))


def delete_message_view(request, section_id, topic_id, message_id):
    message = Message.objects.filter(message_id=message_id)[:1].get()
    if not request.user.is_authenticated() or \
            (request.user.username != 'admin' and request.user.username != message.user_name):
        return HttpResponse('Access denied.')

    topic = Topic.objects.filter(topic_id=topic_id)[:1].get()
    topic.modification_date = django.utils.timezone.now()
    topic.save()

    Message.objects.filter(message_id=message_id).delete()

    return HttpResponseRedirect(reverse('forum:topic', kwargs={'section_id': section_id, 'topic_id': topic_id}))


def modification_date_view(request, topic_id):
    if not Topic.objects.filter(topic_id=topic_id).exists():
        return HttpResponse('topic deleted')
    return HttpResponse(Topic.objects.filter(topic_id=topic_id)[:1].get().modification_date)