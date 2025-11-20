from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from .forms import SignupForm, LoginForm
from .models import User, Email
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            mobile = form.cleaned_data.get('mobile')
            password = form.cleaned_data.get('password')

            User.objects.create_user(email=email, mobile=mobile, password=password)
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data.get('email_or_mobile')
            password = form.cleaned_data.get('password')

            # login using email
            user = authenticate(request, username=user_input, password=password)

            # login using mobile
            if user is None:
                try:
                    mobile_user = User.objects.get(mobile=user_input)
                    user = authenticate(request, username=mobile_user.email, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                login(request, user)
                return redirect("dashboard")

            form.add_error(None, "Invalid credentials")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard(request):
    return render(request, "home.html")


@login_required
def compose(request):
    if request.method == "POST":
        recipients_raw = request.POST.get("recipients")
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        # Parse recipients
        recipients_list = [email.strip() for email in recipients_raw.split(",")]

        # Validate recipients
        recipients = []
        for email in recipients_list:
            try:
                user = User.objects.get(email=email)
                recipients.append(user)
            except User.DoesNotExist:
                messages.error(request, f"User {email} does not exist")
                return redirect("compose")

        # Create email
        email_obj = Email.objects.create(
            sender=request.user,
            subject=subject,
            body=body
        )
        email_obj.recipients.set(recipients)

        messages.success(request, "Email sent successfully")
        return redirect("sent")

    return render(request, "mail/compose.html")


@login_required
def inbox(request):
    emails = Email.objects.filter(
        recipients=request.user,
        trash=False,
        draft=False,
        archived=False
    ).order_by("-timestamp")

    return render(request, "mail/inbox.html", {"emails": emails})


@login_required
def sent(request):
    emails = Email.objects.filter(
        sender=request.user,
        draft=False,
        trash=False
    ).order_by("-timestamp")

    return render(request, "mail/sent.html", {"emails": emails})


@login_required
@csrf_exempt
def mark_read(request, email_id):
    email = Email.objects.get(id=email_id)
    email.read = True
    email.save()
    return JsonResponse({"status": "ok"})


@login_required
def toggle_read(request, email_id):
    email = Email.objects.get(id=email_id)

    # Only recipients can mark read
    if request.user in email.recipients.all():
        email.read = not email.read
        email.save()

    return redirect("inbox")
