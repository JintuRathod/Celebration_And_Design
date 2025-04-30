from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomerRegistrationForm
# from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.contrib.auth.hashers import check_password
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
import random
from reportlab.pdfgen import canvas
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import authenticate, login



#views

def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            messages.error(request, "User already exists or invalid data")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['pass']
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password_hash):
                # Create a Django User object manually or map Customer model properly
                user = authenticate(request, username=customer.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect('events')
                else:
                    # manual fallback (you can improve here)
                    request.session['customer_id'] = customer.customer_id
                    request.session['username'] = customer.username
                    messages.success(request, "Login successful!")
                    return redirect('events')
            else:
                messages.error(request, "Invalid credentials!")
        except Customer.DoesNotExist:
            messages.error(request, "User does not exist!")

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('/')

otp_storage = {}
def custom_password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            customer = Customer.objects.get(email=email)
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp

            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                "210390107052@saffrony.ac.in",
                [email],
                fail_silently=False,
            )
            messages.success(request, "OTP sent to your email.")
            return redirect("password_reset_otp")

        except Customer.DoesNotExist:
            messages.error(request, "Email not found. Please enter a registered email.")

    return render(request, "password_reset_form.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        entered_otp = request.POST.get("otp")

        if email in otp_storage and otp_storage[email] == int(entered_otp):
            messages.success(request, "OTP verified. You can now reset your password.")
            return redirect("password_reset_confirm")

        messages.error(request, "Invalid OTP. Try again.")

    return render(request, "password_reset_otp.html")

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")

        try:
            customer = Customer.objects.get(email=email)
            customer.password_hash = new_password
            customer.save()

            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect("login")

        except Customer.DoesNotExist:
            messages.error(request, "Something went wrong. Try again.")

    return render(request, "password_reset_confirm.html")


def contact(request):
    return render(request, "contact.html")

def review_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        venue = request.POST.get('venue', '')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        Review.objects.create(name=name, email=email, venue=venue, phone=phone, message=message)
        return redirect('contact')

    return render(request, 'review_form.html')


def events(request):
    event_categories = EventCategory.objects.all()
    return render(request, 'events.html', {'event_categories': event_categories})


def event(request):
    return render(request, "event.html")

def book(request):
    return render(request, "book.html")


def plans_view(request):
    event_name = request.GET.get('event_name')
    print(event_name,"Event")
    selected_event = EventCategory.objects.get(category_name = event_name)
    plans = Plan.objects.filter(event  = selected_event)
    return render(request, 'plans.html', {'plans': plans})

def special_request_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        venue = request.POST.get("venue")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found. Please register first.")
            return redirect('register')

        event, created = Event.objects.get_or_create(event_name="-", category=None)

        SpecialRequest.objects.create(
            customer=customer,
            event=event,
            request_text=message,
        )

        if "contact" in request.META['HTTP_REFERER']:
            return redirect('contact')
        else:
            return redirect('events')

    return render(request, "events.html")

def book_event(request):
    if not request.session.get('customer_id'):
        return redirect(f'/login/?next={request.path}')

    plan_id = request.GET.get('plan_id')
    plan = get_object_or_404(Plan, id=plan_id)
    return render(request, 'book.html', {'plan': plan})


@csrf_exempt
def process_booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.content_type == "application/json" else request.POST
            if "razorpay_payment_id" in data and "razorpay_order_id" in data:
                razorpay_payment_id = data["razorpay_payment_id"]
                razorpay_order_id = data["razorpay_order_id"]

                try:
                    payment = Payment.objects.get(order_id=razorpay_order_id)
                    payment.payment_id = razorpay_payment_id
                    payment.save()
                    print("Payment Updated Successfully:", payment.payment_id)
                    return JsonResponse({"success": True})
                except Payment.DoesNotExist:
                    print(" Payment record not found for Order ID:", razorpay_order_id)
                    return JsonResponse({"error": "Payment record not found!"}, status=400)

            first_name = data.get("billing_first_name")
            last_name = data.get("billing_last_name")
            email = data.get("billing_email")
            phone = data.get("billing_phone")
            event_name = data.get("event_name")
            event_start_date = data.get("event_start_date")
            event_end_date = data.get("event_end_date")
            amount = float(data.get("event_price"))

            previous_orders = Payment.objects.filter(customer_email=email).count()
            if previous_orders >= 1:
                amount -= amount * 0.10

            amount_paise = int(amount * 100)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": "1"
            })

            Payment.objects.create(
                customer_first_name=first_name,
                customer_last_name=last_name,
                customer_email=email,
                customer_phone=phone,
                event_name=event_name,
                event_start_date=event_start_date,
                event_end_date=event_end_date,
            amount=amount,
                order_id=payment_order["id"]
            )

            return JsonResponse({
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": amount_paise,
                "order_id": payment_order["id"],
                "discount_applied": previous_orders >= 1
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data!"}, status=400)
        except Exception as e:
            print(" Error:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def check_orders(request):
    email = request.GET.get("email")
    if email:
        previous_orders = Payment.objects.filter(customer_email=email).count()
        return JsonResponse({"previous_orders": previous_orders})
    return JsonResponse({"error": "Email not provided"}, status=400)

def payment_success(request):
    return render(request,"payment_success.html")

def allplan(request):
    plans = Plan.objects.all()
    return render(request, 'allplan.html', {'plans': plans})

def payment_success(request):
    customer_name = request.GET.get("name", "Customer")
    event_name = request.GET.get("event", "Event")
    amount = request.GET.get("amount")

    return render(request, "success.html", {
        "customer_name": customer_name,
        "event_name": event_name,
        'amount': amount
    })
def generate_receipt(request):
    customer_name = request.GET.get("name", "Customer")
    event_name = request.GET.get("event", "Event")
    price = request.GET.get("price")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{customer_name}.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setTitle("Payment Receipt")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 750, "Payment Receipt")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 700, f"Customer Name: {customer_name}")
    pdf.drawString(100, 680, f"Event: {event_name}")
    pdf.drawString(100, 660, f"Amount Paid: Rs. {price}")

    pdf.showPage()
    pdf.save()

    return response

def reset_password_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            customer = Customer.objects.get(email=email)
            token = get_random_string(length=32)
            customer.reset_token = token
            customer.save()
            reset_link = request.build_absolute_uri(f"/reset-password-confirm/{token}/")
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return render(request, "reset_form.html", {"message": "Email sent!"})
        except Customer.DoesNotExist:
            return render(request, "reset_form.html", {"error": "Email not found!"})

    return render(request, "password_reset_request.html")

def reset_password_confirm(request, token):
    try:
        customer = Customer.objects.get(reset_token=token)
    except Customer.DoesNotExist:
        return HttpResponse("Invalid or expired token.")

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            customer.password_hash = make_password(new_password)
            customer.reset_token = None
            customer.save()
            return redirect('login')

    return render(request, 'reset_confirm.html', {'token': token})

