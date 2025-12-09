# core/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .forms import ResumeUploadForm, JobDescriptionForm, SignUpForm
from .models import Resume, JobDescription, Analysis, Profile
from .utils import extract_text_from_file, compute_alignment_score, suggest_improvements
from .github_helper import search_github_repos


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/home.html")


def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create profile (if you have a Profile model that stores extra info)
            try:
                Profile.objects.create(user=user)
            except Exception:
                # ignore if profile creation fails or model not present/ready
                pass
            # log the user in
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    # Redirect authenticated users away from the login page
    if request.user.is_authenticated:
        return redirect("dashboard")

    next_url = request.GET.get("next") or request.POST.get("next") or None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            # use the imported `login` (not auth_login)
            login(request, user)
            # Security: only redirect to safe internal urls
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("dashboard")
        messages.error(request, "Invalid credentials")

    return render(request, "core/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    analyses = Analysis.objects.filter(resume__user=request.user).order_by("-created_at")[:5]
    return render(request, "core/dashboard.html", {"resumes": resumes, "analyses": analyses})


@login_required
def upload_resume(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            r = form.save(commit=False)
            r.user = request.user
            r.save()
            # Extract text from file, save back on resume
            try:
                path = r.file.path
                text = extract_text_from_file(path, r.file.name)
                r.text = text
                r.save()
            except Exception as e:
                # If extraction fails, keep file saved but notify user
                messages.warning(request, "Resume uploaded but processing failed.")
            else:
                messages.success(request, "Resume uploaded and processed.")
            return redirect("dashboard")
    else:
        form = ResumeUploadForm()
    return render(request, "core/upload_resume.html", {"form": form})


@login_required
def analyze(request, resume_id=None):
    if request.method == "POST":
        jd_form = JobDescriptionForm(request.POST)
        if jd_form.is_valid():
            jd = jd_form.save(commit=False)
            jd.user = request.user
            jd.save()

            # pick resume: either provided by id or the latest uploaded
            if resume_id:
                resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            else:
                resume = Resume.objects.filter(user=request.user).order_by("-uploaded_at").first()

            # If no resume exists, show a message and redirect user to upload
            if not resume:
                messages.warning(request, "No resume found — please upload one before analyzing.")
                return redirect("upload_resume")

            resume_text = resume.text or ""
            score = compute_alignment_score(resume_text, jd.text)
            suggestions = suggest_improvements(resume_text, jd.text)
            email_draft = (
                f"Hello Hiring Team,\n\n"
                f"I am applying for the position \"{jd.title}\". I have experience relevant to this role, including ...\n\n"
                f"Highlights:\n- Add your top 2-3 achievements here\n\nBest regards,\n{request.user.get_full_name() or request.user.username}"
            )

            # Build keywords and search GitHub (helper returns list/dict expected by model)
            keywords = jd.title + " " + " ".join(jd.text.split()[:40])
            try:
                github_matches = search_github_repos(keywords)
            except Exception:
                github_matches = []

            a = Analysis.objects.create(
                resume=resume,
                jd=jd,
                score=score,
                suggestions=suggestions,
                email_draft=email_draft,
                github_matches=github_matches,
            )
            # Redirect to analysis result
            return redirect("analysis_result", a.id)
    else:
        jd_form = JobDescriptionForm()

    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "core/analyze.html", {"form": jd_form, "resumes": resumes})


@login_required
def analysis_result(request, analysis_id):
    a = get_object_or_404(Analysis, id=analysis_id, resume__user=request.user)
    return render(request, "core/analyze_result.html", {"analysis": a})


@login_required
def send_email(request, analysis_id):
    a = get_object_or_404(Analysis, id=analysis_id, resume__user=request.user)
    if request.method == "POST":
        to_email = request.POST.get("to_email")
        subject = f"Application for {a.jd.title} - {request.user.get_full_name() or request.user.username}"
        try:
            send_mail(subject, a.email_draft, settings.DEFAULT_FROM_EMAIL, [to_email])
            messages.success(request, "Email sent (console backend).")
        except Exception:
            messages.error(request, "Failed to send email.")
        return redirect("analysis_result", analysis_id=analysis_id)
    return render(request, "core/send_email.html", {"analysis": a})
