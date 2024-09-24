import logging
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.views.generic import FormView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from axes.decorators import axes_dispatch
from braces.views import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from apps.core.utils import to_mg
from django.urls import reverse_lazy
from .forms import UserSettingsForm
from .models import UserSettings, UserWalletAddress
import random
import string


logger = logging.getLogger(__name__)



@login_required
def logout_view(request):
    logout(request)
    response = redirect(reverse_lazy('login'))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@csrf_exempt
@axes_dispatch
def login_view(request):
    # Force logout.
    logout(request)
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')
        print(password)
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/dashboard/')
    return render(request, 'pages/authentication/signin/illustration.html')

@csrf_exempt
@axes_dispatch
def signin_with_wallet(request):
    if request.method == 'POST':
        wallet_address = request.POST.get('wallet_address')
        print("Wallet address: %s" % wallet_address)
        if wallet_address:
            # Look for a user associated with this wallet address
            try:
                wallet = UserWalletAddress.objects.get(address=wallet_address)
                user = wallet.user
                
                # Log the user in
                login(request, user)
                messages.success(request, 'Successfully signed in with wallet.')
                return redirect('dashboard')  # Redirect to the user's dashboard or desired page
            except UserWalletAddress.DoesNotExist:
                messages.error(request, 'Wallet address not found.')
        else:
            messages.error(request, 'No wallet address provided.')

    return redirect('login')

@csrf_exempt
@login_required

def create_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        primary_phone = request.POST.get('primary_phone')
        secondary_phone = request.POST.get('secondary_phone', None)
        date_of_birth = request.POST.get('date_of_birth', None)
        address = request.POST.get('address', None)

        # Basic validation
        if not email or not first_name or not last_name:
            messages.error(request, 'All fields are required.')
            return render(request, 'pages/pages/users/new-user.html')  # Return to the same form with error message
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return render(request, 'pages/pages/users/new-user.html')  # Return to the same form with error message
        
        # Generate a username and password
        username = email.split('@')[0]
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(8))
        
        # Create the user
        user = User.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        user.set_password(password)
        user.save()
        
        user_settings = UserSettings(user=user)
        user_settings.primary_phone = primary_phone
        user_settings.secondary_phone = secondary_phone
        user_settings.date_of_birth = date_of_birth
        user_settings.address = address
        user_settings.save()
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = request.build_absolute_uri(reverse('set_password') + f'?uidb64={uidb64}&token={token}')
        
        try:
            send_mail(
                'Your Temporary Password',
                f'Hello {first_name},\n\nYour account has been created successfully. Here is your temporary password: {password}\n\nPlease change your password using the link below:\n{reset_link}.\n\nBest regards,\nYour Company',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'User Created Successfully! A temporary password has been sent to the user\'s email.')
            return redirect('users_list')
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            messages.error(request, 'User created but failed to send email. Please contact support.')
            return render(request, 'pages/pages/users/new-user.html')  # Return to the same form with error message

    return render(request, 'pages/pages/users/new-user.html')

@login_required
def update_user(request):
    user = get_object_or_404(User, pk=request.user.pk)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.settings.primary_phone = request.POST.get('primary_phone')
        user.settings.secondary_phone = request.POST.get('secondary_phone')
        user.settings.date_of_birth = request.POST.get('date_of_birth')
        user.settings.address = request.POST.get('address')
        user.save()
        user.settings.save()
        messages.success(request, 'User profile updated successfully.')
        return redirect('usersettings')
    return render(request, 'pages/pages/account/settings.html', {'user': user})

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'pages/pages/account/settings.html')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'pages/pages/account/settings.html')

        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password has been updated successfully.')
        return redirect('usersettings')

    return render(request, 'pages/pages/account/settings.html')

@login_required
def update_wallet_address(request):
    user = request.user
    wallet_address, created = UserWalletAddress.objects.get_or_create(user=user)

    if request.method == 'POST':
        address = request.POST.get('wallet_address')
        provider = request.POST.get('wallet_provider')

        if address and provider:
            wallet_address.address = address
            wallet_address.provider = provider
            wallet_address.save()
            messages.success(request, 'Wallet address updated successfully.')
        else:
            messages.error(request, 'Please provide both a wallet address and provider.')

        return redirect('usersettings')

    # Render template with the current wallet address (if any)
    context = {
        'user': user,
        'wallet_address': wallet_address
    }
    return render(request, 'pages/pages/account/settings.html', context)

@login_required
def disconnect_wallet(request):
    # Get the wallet address for the logged-in user
    wallet_address = UserWalletAddress.objects.filter(user=request.user).first()

    # If a wallet is connected, clear the wallet address and provider
    if wallet_address and wallet_address.address:
        wallet_address.address = ""
        wallet_address.provider = ""
        wallet_address.save()
        messages.success(request, "Wallet disconnected successfully.")
    else:
        messages.error(request, "No wallet connected to disconnect.")

    return redirect('usersettings') 


def delete_user(request):
    user = get_object_or_404(User, pk=request.user.pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('login')
    return render(request, 'pages/pages/account/settings.html', {'user': user})

class UserSettingsView(LoginRequiredMixin, FormView):
    success_url = '.'
    form_class = UserSettingsForm
    template_name = 'pages/pages/account/settings.html'
    login_url = '/accounts/login/'

    def get_initial(self):
        user = self.request.user
        settings = user.settings

        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Settings Saved!')

        return super(UserSettingsView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            user.settings.time_zone = form.cleaned_data['time_zone']
            user.settings.save()

            logger.info('Account Settings updated by %s', user)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
@login_required
def users_list(request):
    users = User.objects.all()
    return render(request, 'pages/pages/users/list.html', {'users': users})

@csrf_exempt
def set_password(request):
    uidb64 = request.GET.get('uidb64')
    token = request.GET.get('token')

    if request.method != 'POST':
        if uidb64 and token:
            try:
                uid = urlsafe_base64_decode(uidb64).decode('utf-8')
                user = User.objects.get(pk=uid)
                token_generator = PasswordResetTokenGenerator()
                if token_generator.check_token(user, token):
                    return render(request, 'pages/authentication/set/set_password.html', {'uidb64': uidb64, 'token': token})
            except (ValueError, OverflowError, User.DoesNotExist):
                messages.error(request, 'Invalid token or user.')
        return redirect('login')  # Redirect if no valid uidb64 and token

    new_password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    
    print(new_password)
    print(confirm_password)

    if not uidb64 or not token:
        messages.error(request, 'Invalid request.')
        return redirect('login')

    token_generator = PasswordResetTokenGenerator()
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = User.objects.get(id=uid)
    except (ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid user.')
        return redirect('login')

    if user and token_generator.check_token(user, token):
        if not new_password or not confirm_password:
            messages.error(request, 'Both password fields are required.')
            return render(request, 'pages/authentication/set/set_password.html', {'uidb64': uidb64, 'token': token})
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'pages/authentication/set/set_password.html', {'uidb64': uidb64, 'token': token})

        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password changed successfully. You can now log in.')
        return redirect('login')

    messages.error(request, 'Invalid token.')
    return redirect('login')

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            subject = 'Password Reset Request'
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = request.build_absolute_uri(reverse('set_password') + f'?uidb64={uidb64}&token={token}')
            
            message = f'Hello {user.first_name} {user.last_name},\n\nPlease change your password using the link below:\n{reset_link}.\n\nBest regards,\nYour Company'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('check_email')
        except User.DoesNotExist:
           messages.error(request, 'No user found with this email address.') 
    return render(request, 'pages/authentication/reset/illustration.html')