# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return f"Resume {self.user.username} {self.uploaded_at.date()}"

class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JD: {self.title} by {self.user.username}"

class Analysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    jd = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    score = models.FloatField()
    suggestions = models.TextField()
    email_draft = models.TextField()
    github_matches = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.resume.user.username} - {self.jd.title}"