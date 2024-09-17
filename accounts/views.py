from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegisterForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth import login, logout
from django.contrib.auth import  update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import  PasswordChangeForm
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.views.generic import FormView
from django.template.loader import render_to_string
from .forms import UserUpdateForm
from django.views import View
# Create your views here.
def send_transaction_email(user,  subject, template):
        message = render_to_string(template, {
            'user' : user,
            
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
class UserRegistrationViews(FormView):
    template_name= 'accounts/user_register.html'
    form_class=UserRegisterForm
    success_url=reverse_lazy('register')
    def form_valid(self, form):
        user=form.save()
        login(self.request,user)
        return super().form_valid(form)

class UserLoginViews(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

    
class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.post(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        return reverse_lazy('home')

class PassChangeView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'accounts/pass_change.html'
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Password Updated Successfully')
        send_transaction_email(self.request.user,  "Password Change Message", "transactions/pass_email.html")
        return super().form_valid(form)
class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
        return render(request, self.template_name, {'form': form})