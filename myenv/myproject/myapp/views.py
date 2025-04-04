from django.shortcuts import render, redirect, get_object_or_404
from.models import *
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from.models import User
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from.models import Car
from.models import Review
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import razorpay
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.utils import ImageReader
from .models import Booking 

from django.contrib.auth.hashers import make_password

from django.utils.timezone import now
import datetime
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# Create your views here.

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        try:
         user = User.objects.get(email=request.POST['email'])
         msg = "Email already exists!!"
         return render(request, 'signup.html', {'msg': msg})
        except User.DoesNotExist:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    name=request.POST['name'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    password=request.POST['password'],
                    profile=request.FILES['profile'],
                    usertype=request.POST['usertype']
                )
                msg = "Signup Successfully!!"
                return render(request, 'login.html', {'msg': msg})
            else:
                msg = "Password & confirm password do not match!!"
                return render(request, 'signup.html', {'msg': msg})
    else:
        return render(request, 'signup.html')

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['profile'] = user.profile.url
                if user.usertype == "customer":
                    return redirect('index')
                else:
                    return redirect('lindex')
            else:
                msg = "Invalid Password!!"
                return render(request, 'login.html', {'msg': msg})
        except User.DoesNotExist:
            msg = "Invalid Email!!"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')

def logout(request):
    request.session.pop('email', None)  # Remove 'email' if it exists
    request.session.pop('profile', None)  # Remove 'profile' if it exists
    return redirect('login')

def cpass(request):
    if request.method=="POST":
        user = User.objects.get(email=request.session['email'])

        if user.password == request.POST['opassword']:
            if request.POST['npassword']==request.POST['cnpassword']:
                user.password = request.POST['npassword']
                user.save()

                return redirect('logout')


            else:
                msg = "New password & confirm new password does not match!!"
                return render(request,'cpass.html',{'msg':msg})

        else:
            msg = "Old password does not match!!"
            return render(request,'cpass.html',{'msg':msg})
        



    else:
        return render(request,'cpass.html')
    

    
def fpass(request):
    if request.method=="POST":
        try:
            email = request.POST.get('email')
            user = User.objects.get(email=email)
            otp = random.randint(1000,9999)
            subject = "Password Reset OTP"
            message = f"your OTP is {otp}"
            email_from = settings.EMAIL_HOST_USER
            receipent_list = [user.email]
            send_mail(subject,message,email_from,receipent_list)
            request.session['email'] = user.email
            request.session['otp'] = otp
            return render(request,'otp.html')
        except User.DoesNotExist: 
            msg="Invalid email id"
            return render(request,'fpass.html',{'msg':msg})
        
    return render(request,'fpass.html')

def otp(request):
    if request.method=="POST":
        try:
           otp = int(request.session.get('otp', 0)) 
           uotp = int(request.POST.get('uotp', 0)) 
           if otp == uotp:
                del request.session['otp']
                return render(request,'newpass.html')
           else:
                msg="Invalid OTP"
                return render(request,'otp.html',{'msg':msg})
        except(ValueError,TypeError):
            msg="An error occured.Please try again."
            return render(request,'otp.html',{'msg':msg})
    return render(request,'otp.html')


def newpass(request):
    if request.method=="POST":
        try:
            email = request.session['email']
            user = User.objects.get(email=email)
            npassword = request.POST['npassword']
            cnpassword = request.POST['cnpassword']
            if npassword == cnpassword:
               user.password = make_password(npassword)
               user.save()
               del request.session['email']
               return redirect('login')
            
            else:
                msg="Password and confirm password do not match"
                return render(request,'newpass.html',{'msg':msg})
        except User.DoesNotExist:
            msg="User not found.Please try again."
            return render(request,'newpass.html',{'msg':msg})
        
    return render(request,'newpass.html')

def uprofile(request):
    try:
        user = User.objects.get(email=request.session['email'])
    except User.DoesNotExist:
        return redirect('login')  # Redirect if user not found (session expired, etc.)

    if request.method == "POST":
        user.name = request.POST.get('name', user.name)  # Use `.get()` to avoid KeyError
        user.mobile = request.POST.get('mobile', user.mobile)

        # Save the user details first
        user.save()

        # Handle profile picture update safely
        if 'profile' in request.FILES:
            user.profile = request.FILES['profile']
            user.save()
            request.session['profile'] = user.profile.url  # Update session with new image

        return redirect('index')  # Redirect to home after updating profile

    return render(request, 'uprofile.html', {'user': user})

def carsingle(request):
    return render(request, 'car/carsingle.html')
       

def about(request):
    return render(request, 'about.html')




def details(request, pk):
    car = Car.objects.get(pk=pk)
    related_reviews = Review.objects.filter(car=car).order_by('-created_at')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        if rating and review_text:
            Review.objects.create(
                car=car,
                user=request.user,
                rating=int(rating),
                review=review_text
            )
            return redirect('details', pk=car.pk)
        return render(request, 'details.html', {
            'car': car,
            'related_reviews': related_reviews,
            'error': 'Invalid review data'
        })

    return render(request, 'details.html', {
        'car': car,
        'related_reviews': related_reviews
    })


def blog(request):
    return render(request, 'blog.html')

def blogsingle(request):
    return render(request, 'blogsingle.html')


def car(request):
    try:
        query = request.GET.get('q', '')  # Safely get 'q'
        print("Received Query:", query)  # Debugging output
        if query:
            car = Car.objects.filter(cname__icontains=query)
        else:
            car = Car.objects.all()
        return render(request, 'car.html', {'car': car})
    except Exception as e:
        print("Error:", e)
        msg = "Please Login First!"
        return render(request, 'login.html',{'msg':msg})



def pricing(request):
    return render(request, 'pricing.html')

def services(request):
    return render(request, 'services.html')

def lindex(request):
    return render(request, 'lindex.html')

def add(request):
    if request.method == "POST":
        lessor = User.objects.get(email=request.session['email'])  # ✅ Correct variable name
        try:
            Car.objects.create(
                lessor=lessor,  # ✅ Correct field name
                stransmission=request.POST['stransmission'],
                sfuel=request.POST['sfuel'],
                cname=request.POST['cname'],
                milegae=request.POST['milegae'],
                seats=request.POST['seats'],
                
                luggage=request.POST['luggage'],
                desc=request.POST['desc'],
                cprice=request.POST['cprice'],
                cimage=request.FILES['cimage']
            )
            msg = "Car Added Successfully!!"
            return redirect('view')
        except Exception as e:
            print("**********************", e)
            return redirect('lindex')
    else:
        return render(request, 'add.html')


def view(request):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.filter(lessor=lessor)
   
    return render(request, 'view.html', {'car': car})



def update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.cname = request.POST.get('cname')
        car.cprice = request.POST.get('cprice')
        car.milegae = request.POST.get('milegae')
        car.stransmission = request.POST.get('stransmission')
        car.seats = request.POST.get('seats')
        car.luggage = request.POST.get('luggage')
        car.sfuel = request.POST.get('sfuel')
        car.desc = request.POST.get('desc')
        if 'cimage' in request.FILES:
            car.cimage = request.FILES['cimage']
        try:
            if not car.cname or not car.cprice:
                raise ValueError("Car name and price are required.")
            car.cprice = float(car.cprice)
            car.seats = int(car.seats) if car.seats else None
            car.luggage = int(car.luggage) if car.luggage else None
            car.save()
            messages.success(request, f"'{car.cname}' updated successfully!")
            return redirect('view')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "An error occurred while updating the car.")
    return render(request, 'update.html', {'car': car})

def delete(request,pk):
    lessor = User.objects.get(email=request.session['email'])
    car = Car.objects.get(pk=pk)
    car.delete()
    return redirect('view')

def cart(request, pk):
    try:
        user = User.objects.get(email=request.session['email'])
        car = Car.objects.get(pk=pk)

        if request.method == "POST":
            # Validate total_days
            total_days_str = request.POST.get('total_days', '')

            if not total_days_str:
                messages.error(request, "Total days cannot be empty")
                return render(request, 'cart.html', {'car': car, 'user': user, 'error': "Please select valid dates"})

            try:
                total_days = int(total_days_str)
                if total_days <= 0:
                    messages.error(request, "Total days must be at least 1")
                    return render(request, 'cart.html', {'car': car, 'user': user, 'error': "Total days must be at least 1"})
            except ValueError:
                messages.error(request, "Invalid value for total days")
                return render(request, 'cart.html', {'car': car, 'user': user, 'error': "Please enter a valid number for total days"})

            # Validate start_date & end_date
            start_date_str = request.POST.get('start_date', '')
            end_date_str = request.POST.get('end_date', '')

            if not start_date_str or not end_date_str:
                messages.error(request, "Both start date and end date are required")
                return render(request, 'cart.html', {'car': car, 'user': user, 'error': "Please select valid dates"})

            try:
                # Use datetime.datetime.strptime instead of datetime.strptime
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

                if end_date < start_date:
                    messages.error(request, "End date cannot be before start date")
                    return render(request, 'cart.html', {'car': car, 'user': user, 'error': "End date must be after start date"})
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD")
                return render(request, 'cart.html', {'car': car, 'user': user, 'error': "Invalid date format"})

            # Calculate total amount
            total_amount = total_days * car.cprice

            # Create booking
            booking = Booking.objects.create(
                user=user,
                car=car,
                pickup_address=request.POST.get('pickup_address', ''),
                drop_address=request.POST.get('drop_address', ''),
                start_date=start_date,
                end_date=end_date,
                pick_time=request.POST.get('pick_time', ''),
                total_days=total_days,
                total_amount=total_amount,
                status=False  # Default to pending
            )

            return redirect('summary', pk=booking.id)  # Redirect to summary page
        else:
            return render(request, 'cart.html', {'car': car, 'user': user})

    except KeyError as e:
        print(f"Session key error: {e}")
        messages.error(request, "Please login first")
        return render(request, 'login.html', {'msg': "Please login first"})
    except User.DoesNotExist:
        messages.error(request, "User account not found")
        return render(request, 'login.html', {'msg': "User account not found. Please login again."})
    except Car.DoesNotExist:
        messages.error(request, "Car not found")
        return redirect('index')
    except Exception as e:
        print(f"Error in cart view: {e}")
        messages.error(request, "An error occurred. Please try again.")
        return render(request, 'cart.html', {'car': car, 'user': user, 'error': "An error occurred. Please try again."})
    


def summary(request, pk):  # pk is now booking_id
    try:
        if 'email' not in request.session:
            return render(request, 'login.html', {'msg': "Please login first"})
        user = get_object_or_404(User, email=request.session['email'])
        booking = get_object_or_404(Booking, id=pk, user=user)
        car = booking.car

        net = int(booking.total_amount * 100)  # Convert to paise
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            'amount': net,
            'currency': 'INR',
            'payment_capture': '1'
        })

        context = {
            'car': car,
            'user': user,
            'booking': booking,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'payment': payment
        }
        return render(request, 'summary.html', context)
    except Exception as e:
        print(f"Error in summary view: {e}")
        return render(request, 'login.html', {'msg': "Something went wrong. Please try again."})
    
def success(request):
    try:
        payment_id = request.GET.get('razorpay_payment_id')
        user = User.objects.get(email=request.session['email'])
        
        # Get the latest booking for this user
        booking = Booking.objects.filter(user=user).order_by('-id').first()
        
        if booking is None:
            messages.error(request, "No booking found")
            return redirect('index')
            
        if not booking.status:  # Only update if unpaid
            booking.payment_id = payment_id
            booking.status = True
            booking.save()
        
        # Make sure we explicitly pass both booking and amount to the template
        context = {
            'booking': booking,
            'amount': booking.total_amount,  # Explicitly include amount
            'payment_id': payment_id
        }
        
        print(f"Debug: Booking amount is {booking.total_amount}")  # Debugging
        
        return render(request, 'success.html', context)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please login again.")
        return redirect('login')
    except Exception as e:
        print(f"Error in success view: {e}")
        messages.error(request, "Something went wrong with your payment")
        return redirect('index')

   
def myorder(request):
    try:
        user = User.objects.get(email=request.session['email'])
        bookings = Booking.objects.filter(user=user).order_by('-id')
        return render(request, 'myorder.html', {'bookings': bookings})
    except User.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')
    except Exception as e:
        print(f"Error in myorder view: {e}")
        messages.error(request, "Something went wrong. Please try again.")
        return redirect('index')

def cancelorder(request, booking_id):
    try:
        user = User.objects.get(email=request.session['email'])
        booking = get_object_or_404(Booking, id=booking_id, user=user)
        
        if request.method == "POST":
            if not booking.status:  # Only cancel if not confirmed (status=False)
                booking.delete()
                messages.success(request, "Order cancelled successfully!")
            else:
                messages.error(request, "Cannot cancel a confirmed booking.")
            return redirect('myorder')
        
        return render(request, 'cancelorder.html', {'booking': booking})
    
    except User.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')
    except Exception as e:
        print(f"Error in cancelorder view: {e}")
        messages.error(request, "Something went wrong. Please try again.")
        return redirect('myorder')
    
def pay(request, booking_id):
    try:
        if 'email' not in request.session:
            return render(request, 'login.html', {'msg': "Please login first"})
        
        # Fetch user and booking
        user = get_object_or_404(User, email=request.session['email'])
        booking = get_object_or_404(Booking, id=booking_id, user=user)
        
        if booking.status:
            messages.error(request, "This booking is already paid.")
            return redirect('myorder')

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Calculate amount in paise
        net = int(booking.total_amount * 100)
        
        # Create Razorpay order
        payment = client.order.create({
            'amount': net,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Context for the payment page
        context = {
            'car': booking.car,
            'user': user,
            'booking': booking,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'payment': payment
        }
        return render(request, 'summary.html', context)  # Reuse summary.html for payment UI

    except Exception as e:
        print(f"Error in pay view: {e}")
        messages.error(request, "Something went wrong. Please try again.")
        return redirect('myorder')
    

def generate_invoice_pdf(request, pk):
    if 'email' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, email=request.session['email'])
    booking = get_object_or_404(Booking, id=pk, user=user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.pk}.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Adding JoyRide Logo
    logo_path = "static/images/logo.png"  # Adjust the path accordingly
    try:
        logo = ImageReader(logo_path)
        p.drawImage(logo, 420, height - 80, width=100, height=50, mask='auto')
    except Exception as e:
        print(f"Error loading logo: {e}")

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Invoice")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 80, f"Booking ID: {booking.id}")
    p.drawString(100, height - 100, f"Date: {booking.start_date.strftime('%Y-%m-%d')}")

    p.drawString(400, height - 50, "Car Rental Co.")
    p.drawString(400, height - 70, "123 Rental Street")
    p.drawString(400, height - 90, "City, State, ZIP")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 140, "Billed To:")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 160, f"{user.name or user.email}")
    p.drawString(100, height - 180, f"{booking.pickup_address}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 220, "Description")
    p.drawString(400, height - 220, "Amount")
    p.line(100, height - 225, 500, height - 225)

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 250, f"Car: {booking.car.cname}")
    p.drawString(400, height - 250, f"₹ {booking.car.cprice} / day")
    p.drawString(100, height - 270, f"Duration: {booking.total_days} days")
    p.drawString(400, height - 270, f"₹ {booking.total_amount}")
    p.drawString(100, height - 290, f"Pickup: {booking.start_date} {booking.pick_time}")
    p.drawString(100, height - 310, f"Dropoff: {booking.end_date}")

    p.line(100, height - 325, 500, height - 325)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, height - 350, f"Total: ₹ {booking.total_amount}")

    p.setFont("Helvetica", 10)
    p.drawString(100, 50, "Thank you for choosing us! Contact support at support@carrental.com")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def uprofilelessor(request):
    try:
        user = User.objects.get(email=request.session['email'])
    except User.DoesNotExist:
        return redirect('login')  # Redirect if user not found (session expired, etc.)

    if request.method == "POST":
        user.name = request.POST.get('name', user.name)  # Use `.get()` to avoid KeyError
        user.mobile = request.POST.get('mobile', user.mobile)

        # Save the user details first
        user.save()

        # Handle profile picture update safely
        if 'profile' in request.FILES:
            user.profile = request.FILES['profile']
            user.save()
            request.session['profile'] = user.profile.url  # Update session with new image

        return redirect('index')  # Redirect to home after updating profile

    return render(request, 'uprofilelessor.html', {'user': user})

