from django.urls import path, re_path
from .views import HelpPageView, MailingListSignupAjaxView

urlpatterns = [
    path('help/', HelpPageView.as_view(), name='help'),
    re_path(r'^mailing-list-signup-ajax-view/$', MailingListSignupAjaxView.as_view(), name='mailing_list_signup_ajax_view'),
]
