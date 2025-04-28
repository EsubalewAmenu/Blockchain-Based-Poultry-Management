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
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('create_user/', create_user, name='create_user'),
    path('password/set/', set_password, name='set_password'),
    path('user/list/', users_list, name='users_list'),
    path('user/update/', update_user, name='update_user'),
    path('user/delete/', delete_user, name='delete_user'),
    path('password/change/', change_password, name='change_password'),
    path('settings/', UserSettingsView.as_view(), name='usersettings'),
    path('user/wallet/update/', update_wallet_address, name='update_wallet_address'),
    path('user/wallet/disconnect', disconnect_wallet, name='disconnect_wallet'),
    path('login/', login_view, name='login'),
    path('tracking/', tracking_view, name='tracking_view'),
    path('signin_with_wallet/', signin_with_wallet, name='signin_with_wallet'),
    path('logout/', logout_view, name='logout'),
    path('reset-password/', reset_password, name='reset_password'),
    

    
    # path('password/change/', password_change, name='password_change'),
    # path('password/change/done/', password_change_done, name='password_change_done'),
    # path('password/reset/', password_reset, name='password_reset'),
    # path('password/reset/done/', password_reset_done, name='password_reset_done'),
    # re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name='password_reset_confirm'),
    # path('password_reset_complete/', password_reset_complete, name='password_reset_complete'),
]
