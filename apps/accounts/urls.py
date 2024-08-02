# from django.contrib.auth.views import (
#     logout,
#     password_change,
#     password_change_done,
#     password_reset,
#     password_reset_done,
#     password_reset_confirm,
#     password_reset_complete
# )
from django.urls import path, re_path
from .views import login_view, UserSettingsView, SignUpView, logout
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('settings/', UserSettingsView.as_view(), name='usersettings'),
    path('login/', login_view, name='login'),
    # path('logout/', logout, {'next_page': '/accounts/login/'}, name='logout'),
    path('logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    
    # path('password/change/', password_change, name='password_change'),
    # path('password/change/done/', password_change_done, name='password_change_done'),
    # path('password/reset/', password_reset, name='password_reset'),
    # path('password/reset/done/', password_reset_done, name='password_reset_done'),
    # re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),
    # path('password_reset_complete/', password_reset_complete, name='password_reset_complete'),
]
