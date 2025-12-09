import random
from django.shortcuts import render,redirect,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.http import  HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import OTPForm, UserProfileForm
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from .models import UserProfile
import os
from reportlab.lib import colors


User = get_user_model()


def next_view(request):
    return render(request, 'next_view.html')

def home(request):
    return render(request, 'home.html')

def ensure_user_profile_exists(user):

    if not hasattr(user, 'userprofile'):
        UserProfile.objects.get_or_create(user=user)


def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

def register(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = generate_otp()
            send_otp_email(email, otp)
            request.session['otp'] = otp
            request.session['email'] = email
            return redirect('verify_otp')
    else:
        form = OTPForm()
    return render(request, 'register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        otp_from_session = request.session.get('otp')
        email = request.session.get('email')

        if otp_input and otp_from_session and int(otp_input) == otp_from_session:
            try:
                user, created = User.objects.get_or_create(email=email)
                login(request, user)


                ensure_user_profile_exists(user)

                request.session.pop('otp', None)
                request.session.pop('email', None)
                return redirect('user_details')
            except User.DoesNotExist:
                return render(request, 'verify_otp.html', {'error': 'User not found'})

        return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')


@login_required
def user_details(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():

            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:

                user_profile = UserProfile(user=request.user)


            user_profile.name = form.cleaned_data.get('name')
            user_profile.father_name = form.cleaned_data.get('father_name')
            user_profile.age = form.cleaned_data.get('age')
            user_profile.dob = form.cleaned_data.get('dob')
            user_profile.address = form.cleaned_data.get('address')


            if form.cleaned_data.get('photo'):
                user_profile.photo = form.cleaned_data.get('photo')
            if form.cleaned_data.get('user_id_proof'):
                user_profile.user_id_proof = form.cleaned_data.get('user_id_proof')

            user_profile.save()
            print(user_profile.name, user_profile.father_name, user_profile.age)

            return redirect('next_view')
    else:
        form = UserProfileForm()

    return render(request, 'user_details.html', {'form': form})


@login_required
def generate_id(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:

        print(f"New profile created for: {user_profile.name}")
    else:

        print(f"Using existing profile for: {user_profile.name}")


    if not user_profile.name or not user_profile.father_name or not user_profile.age:
        print("Warning: User profile is missing important details.")


    return render(request, 'generate_id.html', {
        'user_profile': user_profile,
        'party_name': "Indian National Congress"
    })


@login_required
def download_id(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)


    party_name = "Indian National Congress"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="digital_id.pdf"'


    id_width, id_height = 3.37 * inch, 2.125 * inch
    c = canvas.Canvas(response, pagesize=(id_width, id_height))


    header_color = colors.HexColor("#004b87")
    text_color = colors.HexColor("#333333")
    blue_color = colors.HexColor("#4b92db")


    c.setFillColor(colors.white)
    c.rect(0, 0, id_width, id_height, stroke=1, fill=1)
    c.setFillColor(header_color)
    c.rect(0, id_height - 0.5 * inch, id_width, 0.5 * inch, stroke=0, fill=1)


    logo_y = id_height - 0.5 * inch
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'congress-inc-logo.png')
    logo_x = id_width - 0.6 * inch
    logo_width, logo_height = 0.5 * inch, 0.5 * inch

    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
        except Exception as e:
            print("Error loading logo:", e)


    party_name_x = 0.2 * inch
    party_name_y = id_height - 0.35 * inch
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.white)
    c.drawString(party_name_x, party_name_y, party_name)


    photo_x, photo_y = 0.2 * inch, id_height - 1.4 * inch
    if user_profile.photo and os.path.exists(user_profile.photo.path):
        try:
            c.drawImage(user_profile.photo.path, photo_x, photo_y, width=0.8 * inch, height=0.8 * inch)
        except Exception:
            c.drawString(photo_x, photo_y, "Photo not available")
    else:
        c.drawString(photo_x, photo_y, "No Photo")


    details_x, details_y = 1.2 * inch, id_height - 1 * inch
    line_height = 0.18 * inch
    c.setFillColor(text_color)
    c.setFont("Helvetica", 8)


    c.drawString(details_x, details_y, f"Name: {user_profile.name}")
    c.drawString(details_x, details_y - line_height, f"Father's Name: {user_profile.father_name}")
    c.drawString(details_x, details_y - 2 * line_height, f"Age: {user_profile.age or 'Not provided'}")
    c.drawString(details_x, details_y - 3 * line_height, f"Date of Birth: {user_profile.dob or 'Not provided'}")
    c.drawString(details_x, details_y - 4 * line_height, f"Address: {user_profile.address or 'Not provided'}")


    id_proof_text = "ID Proof: Available" if user_profile.user_id_proof else "ID Proof: Not provided"
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(blue_color)
    c.drawString(details_x, details_y - 5 * line_height, id_proof_text)

    c.showPage()
    c.save()

    return response
