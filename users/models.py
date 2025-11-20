from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email, mobile, password=None):
        if not email and not mobile:
            raise ValueError("User must have email or mobile number")

        email = self.normalize_email(email)
        user = self.model(email=email, mobile=mobile)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile, password):
        user = self.create_user(email=email, mobile=mobile, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'   # login with email
    REQUIRED_FIELDS = ['mobile']

    objects = UserManager()

    def __str__(self):
        return self.email if self.email else self.mobile

    @property
    def is_staff(self):
        return self.is_admin


from django.db import models
from django.conf import settings


class Email(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_emails'
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_emails'
    )
    subject = models.TextField(blank=True)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.subject[:20]}"


class Mailbox(models.Model):
    MAILBOX_TYPES = [
        ('inbox', 'Inbox'),
        ('sent', 'Sent'),
        ('drafts', 'Drafts'),
        ('trash', 'Trash'),
        ('important', 'Important'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    mailbox_type = models.CharField(max_length=20, choices=MAILBOX_TYPES)
    email = models.ForeignKey(Email, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.mailbox_type}"
