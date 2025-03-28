from django.shortcuts import render, redirect, get_object_or_404
from.models import *
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from.models import User
from django.http import JsonResponse,HttpResponse
from.models import Car
from.models import Review
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import razorpay
 

from django.contrib.auth.hashers import make_password

from django.utils.timezone import now
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
    email = request.session.get('email')  # Retrieve email from session

    if not email:  # If email is not found in the session, redirect to login
        return redirect('login')  # Replace 'login' with your actual login route name

    try:
       user = User.objects.get(email=email)  # Try to fetch the user
    except User.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")  # Add error message
            return redirect('login')  # Redirect to login page if the user doesn't exist

    car = Car.objects.all()  # Fetch all car objects
    return render(request, 'car.html', {'car': car}) 



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
        try:
            # Get form data with get() method to avoid MultiValueDictKeyError
            car.cname = request.POST.get('cname', car.cname)
            car.cprice = request.POST.get('cprice', car.cprice)
            car.milegae = request.POST.get('mileage', car.milegae)
            car.stransmission = request.POST.get('stransmission', car.stransmission)
            car.seats = request.POST.get('seats', car.seats)
            car.luggage = request.POST.get('luggage', car.luggage)
            car.sfuel = request.POST.get('sfuel', car.sfuel)
            car.desc = request.POST.get('desc', car.desc)
            
            # Handle image upload if a new image is provided
            if 'cimage' in request.FILES:
                car.cimage = request.FILES['cimage']
            
            car.save()
            messages.success(request, 'Car details updated successfully!')
            return redirect('details', pk=car.id)
            
        except Exception as e:
            messages.error(request, f'Error updating car: {str(e)}')
    
    # For GET requests, just display the form
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
            total_days = int(request.POST['total_days'])
            total_amount = total_days * car.cprice
            booking = Booking.objects.create(
                user=user,
                car=car,
                pickup_address=request.POST['pickup_address'],
                drop_address=request.POST['drop_address'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                pick_time=request.POST['pick_time'],
                total_days=total_days,
                total_amount=total_amount,
                status=False  # Default to pending
            )
            return redirect('summary', pk=booking.id)  # Pass booking ID instead of car ID
        else:
            return render(request, 'cart.html', {'car': car, 'user': user})
    except Exception as e:
        print(f"Error in cart view: {e}")
        messages.error(request, "Please login first")
        return render(request, 'login.html', {'msg': "Please login first"})
    


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
        booking = Booking.objects.filter(user=user).order_by('-id').first()  # Get the latest booking
        
        if booking and not booking.status:  # Only update if unpaid
            booking.payment_id = payment_id
            booking.status = True
            booking.save()
        
        return render(request, 'success.html', {'booking': booking})
    except Exception as e:
        print(f"Error in success view: {e}")
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
    
