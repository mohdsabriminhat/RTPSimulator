from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import Instructor, Visitor, Admin
from .forms import AdminLoginForm
from django.views.decorators.http import require_POST
from django.http import Http404
from datetime import datetime
from .models import AdminNote
from .forms import AdminNoteForm 
import calendar
from .forms import RequestCertForm
from .models import RequestCert
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from django.conf import settings
import os
from PIL import Image
from .models import VisitorSlot


# Signup view
def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        contact = request.POST['contact']
        password = request.POST['password']
        email = request.POST['email']
        username = request.POST['username']
        role = request.POST['role']

        # Check if the username already exists
        if Visitor.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken. Please choose another.")
            return redirect('signup')

        # Hash the password before saving it to the database
        hashed_password = make_password(password)

        if role == 'instructor':
            # Create instructor and save to the database
            instructor = Instructor.objects.create(
                name=name,
                contact=contact,
                password=hashed_password,
                email=email,
                username=username
            )
        elif role == 'visitor':
            # Create visitor and save to the database
            visitor = Visitor.objects.create(
                name=name,
                contact=contact,
                password=hashed_password,
                email=email,
                username=username,
                is_approved=False  # Not approved by default
            )
            messages.info(request, "Signup successful. Please wait to be approved by the admin.")
            return redirect('signup')

        return redirect('login')

    return render(request, 'signup.html')

# Login view

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = None
        role = None

        # Try to find user in Visitor
        try:
            user = Visitor.objects.get(username=username)
            role = 'visitor'
        except Visitor.DoesNotExist:
            # Try to find user in Instructor
            try:
                user = Instructor.objects.get(username=username)
                role = 'instructor'
            except Instructor.DoesNotExist:
                user = None

        if user and check_password(password, user.password):
            if role == 'visitor' and not user.is_approved:
                messages.error(request, "Your account is pending approval by the admin.")
                return redirect('login')

            if role == 'instructor' and not user.is_approved:
                messages.error(request, "Instructor account not approved yet.")
                return redirect('login')

            # Save user session
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = role

            # Redirect based on role
            if role == 'visitor':
                return redirect('homepage')
            elif role == 'instructor':
                return redirect('instructor_homepage')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')

def admin_login(request):
    warning_message = None

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']

            if not email.endswith('@nm.gov.my'):
                warning_message = "Warning: For staff only"
            else:
                admin, created = Admin.objects.get_or_create(
                    email=email,
                    defaults={'name': name, 'password': password}
                )

                if not created:
                    if admin.name != name or admin.password != password:
                        warning_message = "Invalid name or password."
                    else:
                        request.session['admin_name'] = admin.name
                        request.session['user_id'] = admin.email  # Set admin ID
                        request.session['role'] = 'admin'
                        return redirect('admin_homepage')
                else:
                    request.session['admin_name'] = name
                    request.session['user_id'] = email  # Set admin ID
                    request.session['role'] = 'admin'
                    return redirect('admin_homepage')
        else:
            warning_message = "Please fill in all required fields."
    else:
        form = AdminLoginForm()

    return render(request, 'admin_login.html', {
        'form': form,
        'warning_message': warning_message
    })

def admin_logout(request):
    request.session.flush()  
    return redirect('admin_login')

@require_POST
def approve_visitor(request, visitor_id):
    visitor = Visitor.objects.get(id=visitor_id)
    visitor.is_approved = True
    visitor.save()
    return redirect('admin_homepage')


@require_POST
def delete_visitor(request, visitor_id):
    Visitor.objects.get(id=visitor_id).delete()
    return redirect('admin_homepage')

def visitor_management(request):
    if request.session.get('role') != 'admin':
        return redirect('admin_login')  
    visitors = Visitor.objects.all().order_by('-id')

    return render(request, 'visitor_management.html', {'visitors': visitors})

# Function to approve visitor
def approve_visitor(request, id):
    try:
        visitor = Visitor.objects.get(id=id)
    except Visitor.DoesNotExist:
        raise Http404("Visitor not found")
    
    # Set the visitor's status to 'approved'
    visitor.is_approved = True
    visitor.save()

    messages.success(request, f"Visitor {visitor.username} has been approved.")
    return redirect('visitor_management')

# Function to delete visitor
def delete_visitor(request, id):
    try:
        visitor = Visitor.objects.get(id=id)
    except Visitor.DoesNotExist:
        raise Http404("Visitor not found")

    # Delete the visitor
    visitor.delete()

    messages.success(request, f"Visitor {visitor.username} has been deleted.")
    return redirect('visitor_management')


def instructor_management(request):
    if request.session.get('role') != 'admin':
        return redirect('admin_login')  # Make sure only admins can access this page

    instructors = Instructor.objects.all().order_by('-id')  

    return render(request, 'instructor_management.html', {'instructors': instructors})

@require_POST
def approve_instructor(request, id):
    try:
        instructor = Instructor.objects.get(id=id)
    except Instructor.DoesNotExist:
        raise Http404("Instructor not found")

    instructor.is_approved = True
    instructor.save()

    return redirect('instructor_management')

@require_POST
def delete_instructor(request, instructor_id):
    try:
        instructor = Instructor.objects.get(id=instructor_id)
    except Instructor.DoesNotExist:
        raise Http404("Instructor not found")

    instructor.delete()
    return redirect('instructor_management')

def admin_homepage(request):
    admin_name = request.session.get('admin_name')
    if not admin_name:
        print("Admin is not logged in.")
        return redirect('admin_login')
    else:
        print(f"Admin logged in: {admin_name}")

    context = {
        'admin_name': admin_name,
    }

    return render(request, 'admin_homepage.html', context)

def admin_homepage(request):
    if request.session.get('role') != 'admin':
        return redirect('admin_login')

    # Handle POST request for saving notes
    if request.method == 'POST':
        form = AdminNoteForm(request.POST)
        if form.is_valid():
            form.save()

    # Fetch all saved notes
    notes = AdminNote.objects.all()

    # Get the current date and month for the calendar
    today = datetime.today()
    current_month_year = today.strftime("%B %Y")
    cal = calendar.Calendar(firstweekday=6)  # Start the week on Sunday
    month_days = cal.monthdatescalendar(today.year, today.month)

    # Build the calendar data (list of weeks with dates and days)
    calendar_weeks = []
    for week in month_days:
        week_data = []
        for day in week:
            if day.month == today.month:
                day_name = day.strftime("%A")  # Get the name of the day (e.g., Monday)
                week_data.append({'date': day.day, 'day_name': day_name})
            else:
                week_data.append(None)
        calendar_weeks.append(week_data)

    return render(request, 'admin_homepage.html', {
        'admin_name': request.session.get('admin_name'),
        'notes': notes,
        'form': AdminNoteForm(),
        'calendar': calendar_weeks,
        'current_month_year': current_month_year,
        'today': today.isoformat(),
    })


#def test(request):
 #   return render(request, 'test.html')

def profile(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or role != 'visitor':
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    visitor = Visitor.objects.get(id=user_id)

    if request.method == 'POST':
        visitor.name = request.POST['name']
        visitor.email = request.POST['email']
        visitor.contact = request.POST['contact']
        visitor.username = request.POST['username']
        visitor.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'profile.html', {'visitor': visitor})

def instructor_profile(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or role != 'instructor':
        messages.error(request, "Access denied.")
        return redirect('login')

    try:
        instructor = Instructor.objects.get(id=user_id)
    except Instructor.DoesNotExist:
        messages.error(request, "Instructor not found.")
        return redirect('login')

    if request.method == 'POST':
        instructor.name = request.POST.get('name')
        instructor.email = request.POST.get('email')
        instructor.username = request.POST.get('username')
        instructor.contact = request.POST.get('contact')
        instructor.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('instructor_profile')

    return render(request, 'instructor_profile.html', {'instructor': instructor})

def instructor_homepage(request):
    if request.session.get('role') != 'instructor':
        return redirect('login')

    instructor_id = request.session.get('user_id')
    instructor = Instructor.objects.get(id=instructor_id)

    return render(request, 'instructor_homepage.html', {'instructor': instructor})

def request_cert(request):
    if request.method == 'POST':
        form = RequestCertForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your certificate request has been submitted successfully!")
            return redirect('instructor_homepage')  # Replace with your actual URL name
    else:
        form = RequestCertForm()

    return render(request, 'certificate_request_form.html', {'form': form})


def certificate_request_success(request):
    return render(request, 'certificate_request_success.html')


def mainpage(request):
    return render(request, 'mainpage.html')


def certificate_requests_list(request):
    requests = RequestCert.objects.all().order_by('-date_completed')
    return render(request, 'certificate_requests_list.html', {'requests': requests})


@require_POST
def approve_certificate_request(request, id):
    cert = get_object_or_404(RequestCert, id=id)
    cert.status = 'Approved'
    cert.save()
    messages.success(request, "Certificate request approved.")
    return redirect('certificate_request_list')

@require_POST
def reject_certificate_request(request, id):
    cert = get_object_or_404(RequestCert, id=id)
    cert.status = 'Rejected'
    cert.save()
    messages.success(request, "Certificate request rejected.")
    return redirect('certificate_request_list')


@require_POST
def delete_certificate_request(request, id):
    cert = get_object_or_404(RequestCert, id=id)
    cert.delete()
    messages.success(request, "Certificate request deleted.")
    return redirect('certificate_request_list')

#def certificate_requests_list(request):
#    return render(request, 'certificate_requests_list.html')

def admin_profile(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or role != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('admin_login')

    try:
        admin = Admin.objects.get(email=user_id)
    except Admin.DoesNotExist:
        messages.error(request, "Admin not found.")
        return redirect('admin_login')

    if request.method == 'POST':
        admin.name = request.POST['name']
        admin.email = request.POST['email']
        admin.password = request.POST['password']
        admin.save()

        # Update session if email or name changes
        request.session['admin_name'] = admin.name
        request.session['user_id'] = admin.email

        messages.success(request, "Profile updated successfully.")
        return redirect('admin_profile')

    return render(request, 'admin_profile.html', {'admin': admin})


def generate_certificate(request):
    # Check if user is logged in (session-based)
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponse("Unauthorized", status=401)

    # Get user from Visitor model
    visitor = get_object_or_404(Visitor, id=user_id)
    visitor_name = visitor.name

    # Function to break name into lines
    def wrap_text(text, max_length=36):
        words = text.split()  # Split the name by spaces
        lines = []
        current_line = ""

        for word in words:
            # Check if adding this word will exceed the max length
            if len(current_line + " " + word) <= max_length:
                current_line += " " + word if current_line else word
            else:
                # Start a new line if the current one exceeds max length
                lines.append(current_line)
                current_line = word

        # Add the last line
        if current_line:
            lines.append(current_line)
        
        return lines

    # Prepare PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Define path to the background image
    image_path = r'C:\Users\RIC_2\Desktop\wawa\progress\250516\RTPSIMULATOR\RTP_Simulator\static\image\e-cert2.png'

    # Debugging: print image path and check if file exists
    print("Image path:", image_path)
    print("Exists:", os.path.exists(image_path))

    if os.path.exists(image_path):
        pil_image = Image.open(image_path).convert("RGB")  # Convert to RGB
        image_reader = ImageReader(pil_image)
        p.drawImage(image_reader, 0, 0, width=width, height=height)

    # Wrap the name text
    name_lines = wrap_text(visitor_name, max_length=36)

    # Add name lines to the certificate, ensuring they fit within the page
    p.setFont("Helvetica-Bold", 25)
    p.setFillColorRGB(1, 1, 1)  # Set text color to white

    # Starting position for the first line
    y_position = height / 2 + 115

    # Draw each line of the name on the certificate
    for line in name_lines:
        p.drawCentredString(width / 2, y_position, line)
        y_position -= 30  # Adjust the position for the next line (move down)

    # Add issue date
    p.setFont("Helvetica", 14)
    today = date.today().strftime('%B %d, %Y')
    p.setFillColorRGB(1, 1, 1)  # Set text color to white (same as name)
    p.drawCentredString(width / 2, y_position - 237, f"Issued on {today}")

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')

def homepage(request):
    # Dapatkan session_key untuk pengunjung
    session_key = request.session.session_key
    
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Semak jika pengunjung sudah ada slot
    slot = VisitorSlot.objects.filter(session_key=session_key).first()
    
    if not slot:
        # Cari slot terakhir yang digunakan dan tambahkan slot baru
        next_slot_number = VisitorSlot.objects.count() + 1
        
        # Cipta slot baru untuk pengunjung ini
        slot = VisitorSlot.objects.create(slot_number=next_slot_number, session_key=session_key)
    
    # Hantar slot_number ke template untuk digunakan dalam iframe
    return render(request, 'homepage.html', {'slot_number': slot.slot_number})


def visitor2(request):
    return render(request, 'visitor2.html')
