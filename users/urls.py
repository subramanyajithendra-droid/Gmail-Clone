from django.urls import path
from . import views
from .views import logout_view, dashboard

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),

    path("compose/", views.compose, name="compose"),
    path("inbox/", views.inbox, name="inbox"),
    path("sent/", views.sent, name="sent"),
    path("email/<int:email_id>/toggle-read/", views.toggle_read, name="toggle_read"),
    path("mark-read/<int:email_id>/", views.mark_read, name="mark_read"),

]