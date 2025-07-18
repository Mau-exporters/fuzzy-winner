from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from datetime import date
import requests
import json
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt  # <--- Added this import
from django.conf import settings  # <--- Added this to use settings variables
from .models import Reservation, Store, Cart, CartItem, Wishlist, Carousel, TeamMember, Feature, FarmStatistic, Event, HeroSlide
from django.core.mail import send_mail
from django.utils import timezone
from .models import OTP
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import make_password
from .models import OTP, User





# ------------------ Helper ------------------ #

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

# ------------------ Static Pages ------------------ #

def home(request):
    is_admin_user = request.user.is_authenticated and request.user.is_staff
    if is_admin_user:
        if request.method == 'POST':
            if 'add_image' in request.POST:
                image = request.FILES.get('image')
                alt_text = request.POST.get('alt_text', '').strip()
                if image and alt_text:
                    Carousel.objects.create(image=image, alt_text=alt_text)
                return redirect('exporters_app:home')

            elif 'delete_image' in request.POST:
                image_id = request.POST.get('delete_image')
                Carousel.objects.filter(id=image_id).delete()
                return redirect('exporters_app:home')

        carousel_images = Carousel.objects.all()
        return render(request, "index.html", {
            "carousel_images": carousel_images,
            "is_admin": True,
        })

    else:
        carousel_images = Carousel.objects.all()
        return render(request, "index.html", {
            "carousel_images": carousel_images,
            "is_admin": False,
        })

def about(request):
    team = TeamMember.objects.all()
    features = Feature.objects.all()
    stats = FarmStatistic.objects.all()
    slides = HeroSlide.objects.all()  # add this line

    context = {
        'team': team,
        'features': features,
        'stats': stats,
        'slides': slides,   # pass slides in context
    }
    return render(request, "about.html", context)

def store(request):
    items = Store.objects.all()
    context = {
        'items': items
    }
    return render(request, "store.html", context)

def team(request):
    if request.method == "POST" and request.user.is_staff:
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name", "").strip()
            role = request.POST.get("role", "").strip()
            details = request.POST.get("details", "").strip()
            is_highlight = "is_highlight" in request.POST
            image = request.FILES.get("image")

            if is_highlight:
                TeamMember.objects.filter(is_highlight=True).update(is_highlight=False)

            if name and role and image:
                TeamMember.objects.create(
                    name=name,
                    role=role,
                    details=details,
                    is_highlight=is_highlight,
                    image=image
                )

        elif action == "update":
            member_id = request.POST.get("member_id")
            member = get_object_or_404(TeamMember, id=member_id)

            member.name = request.POST.get("name", member.name).strip()
            member.role = request.POST.get("role", member.role).strip()
            member.details = request.POST.get("details", member.details).strip()
            is_highlight = "is_highlight" in request.POST

            if is_highlight and not member.is_highlight:
                TeamMember.objects.filter(is_highlight=True).update(is_highlight=False)

            member.is_highlight = is_highlight

            if "image" in request.FILES:
                member.image = request.FILES["image"]

            member.save()

        elif action == "delete":
            member_id = request.POST.get("member_id")
            member = get_object_or_404(TeamMember, id=member_id)
            member.delete()

        return redirect("exporters_app:team")

    members = TeamMember.objects.filter(is_highlight=False)
    highlight = TeamMember.objects.filter(is_highlight=True).first()

    context = {
        "team_members": members,
        "highlight_member": highlight,
        "is_staff": request.user.is_staff
    }
    return render(request, "team.html", context)

def dropdown(request):
    return render(request, "dropdown.html")

def contact(request):
    return render(request, "contact.html")

# ------------------ Booking ------------------ #

def booking(request):
    if request.method == 'POST':
        Reservation.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            people=request.POST.get('people'),
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            message=request.POST.get('message')
        )
        messages.success(request, 'Your table has been booked successfully!')
        return redirect('exporters_app:home')
    return render(request, 'booking.html')

# ------------------ Cart ------------------ #

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Store, pk=item_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {item.name} to your cart.")
    return redirect('exporters_app:store')


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('exporters_app:view_cart')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.select_related('item')

    if request.method == 'POST':
        item_id = request.POST.get('cart_item_id')
        new_quantity = request.POST.get('quantity')

        try:
            # Convert safely in case input is like '720.00'
            new_quantity = int(float(new_quantity))

            cart_item = CartItem.objects.get(id=item_id, cart=cart)

            if new_quantity <= 0:
                cart_item.delete()
                messages.success(request, f"Removed {cart_item.item.name} from your cart.")
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f"Updated quantity for {cart_item.item.name}.")
        except (CartItem.DoesNotExist, ValueError):
            messages.error(request, "Unable to update cart item. Please enter a valid quantity.")

        return redirect('exporters_app:view_cart')

    # Prepare cart data with subtotals
    cart_data = []
    total = 0
    for item in cart_items:
        subtotal = item.quantity * item.item.price
        cart_data.append({
            'id': item.id,
            'item': item.item,
            'quantity': item.quantity,
            'subtotal': subtotal,
        })
        total += subtotal

    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlist_count = wishlist.items.count() if wishlist else 0

    context = {
        'cart_items': cart_data,
        'total': total,
        'cart_count': cart_items.count(),
        'wishlist_count': wishlist_count,
    }
    return render(request, 'cart.html', context)


# ------------------ Wishlist ------------------ #

@login_required
def add_to_wishlist(request, item_id):
    item = get_object_or_404(Store, pk=item_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.items.add(item)
    messages.success(request, f"Added {item.name} to your wishlist.")
    return redirect('exporters_app:store')

@login_required
def remove_from_wishlist(request, item_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    item = get_object_or_404(Store, pk=item_id)
    wishlist.items.remove(item)
    messages.success(request, "Item removed from your wishlist.")
    return redirect('exporters_app:view_wishlist')

@login_required
def view_wishlist(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.all()
    cart_items = CartItem.objects.filter(cart__user=request.user)
    context = {
        'items': items,
        'wishlist_count': items.count(),
        'cart_count': cart_items.count(),
    }
    return render(request, 'wishlist.html', context)

# ------------------ Admin store CRUD ------------------ #

@user_passes_test(is_admin)
def add_store_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        tag = request.POST.get('tag')
        image = request.FILES.get('image')

        Store.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            tag=tag,
            image=image
        )
        messages.success(request, "Farm product added.")
        return redirect('exporters_app:store')

    return render(request, 'store/store_form.html')

@user_passes_test(is_admin)
def edit_store_item(request, item_id):
    item = get_object_or_404(Store, pk=item_id)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.category = request.POST.get('category')
        item.tag = request.POST.get('tag')

        if request.FILES.get('image'):
            item.image = request.FILES['image']

        item.save()
        messages.success(request, "Farm product updated.")
        return redirect('exporters_app:store')

    context = {'item': item}
    return render(request, 'store/store_form.html', context)

@user_passes_test(is_admin)
def delete_store_item(request, item_id):
    item = get_object_or_404(Store, pk=item_id)
    item.delete()
    messages.success(request, "Farm product deleted.")
    return redirect('exporters_app:store')

# ------------------ Events View ------------------ #

def events(request):
    upcoming_events = Event.objects.filter(date__gte=date.today()).order_by('date', 'start_time')
    context = {
        'upcoming_events': upcoming_events
    }
    return render(request, "events.html", context)
class OTPService:
    @staticmethod
    def generate():
        return str(random.randint(100000, 999999))

    @staticmethod
    def send(destination_email, otp_code):
        # Replace with actual email sending logic
        print(f"Sending OTP {otp_code} to {destination_email}")


def auth_view(request):
    step = request.session.get('step', 'login')

    if request.method == 'POST':
        # LOGIN STEP
        if step == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user:
                otp = OTPService.generate()
                OTP.objects.create(
                    user=user,
                    code=otp,
                    purpose='2fa',
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                OTPService.send(user.email, otp)
                request.session['2fa_user_id'] = user.id
                request.session['step'] = 'verify_2fa'
                return redirect('auth_view')
            else:
                messages.error(request, "Invalid credentials")

        # VERIFY 2FA OTP STEP
        elif step == 'verify_2fa':
            otp_code = request.POST.get('otp')
            user_id = request.session.get('2fa_user_id')

            try:
                user = User.objects.get(id=user_id)
                otp_entry = OTP.objects.filter(
                    user=user, code=otp_code, purpose='2fa'
                ).latest('created_at')

                if otp_entry.is_expired():
                    messages.error(request, "OTP expired")
                else:
                    login(request, user)
                    request.session.flush()
                    messages.success(request, "Login successful")
                    return redirect('home')
            except (User.DoesNotExist, OTP.DoesNotExist):
                messages.error(request, "Invalid OTP")

        # REQUEST PASSWORD RESET STEP
        elif step == 'request_password_reset':
            email = request.POST.get('email')
            users = User.objects.filter(email=email)
            if users.count() == 1:
                user = users.first()
                otp = OTPService.generate()
                OTP.objects.create(
                    user=user,
                    code=otp,
                    purpose='reset',
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                OTPService.send(user.email, otp)
                request.session['reset_email'] = email
                request.session['step'] = 'verify_password_reset'
                messages.success(request, "OTP sent to your email.")
                return redirect('exporters_app:auth_view')
            elif users.count() > 1:
                messages.error(request, "Multiple users found with this email. Please contact support.")
            else:
                messages.error(request, "User not found.")

        # VERIFY PASSWORD RESET OTP STEP
        elif step == 'verify_password_reset':
            email = request.POST.get('email')
            otp_code = request.POST.get('otp')

            users = User.objects.filter(email=email)
            if users.count() == 1:
                user = users.first()
                try:
                    otp_entry = OTP.objects.filter(
                        user=user, code=otp_code, purpose='reset'
                    ).latest('created_at')

                    if otp_entry.is_expired():
                        messages.error(request, "OTP expired")
                    else:
                        request.session['reset_user_id'] = user.id
                        request.session['step'] = 'reset_password'
                        messages.success(request, "OTP verified.")
                        return redirect('auth_view')
                except OTP.DoesNotExist:
                    messages.error(request, "Invalid OTP.")
            elif users.count() > 1:
                messages.error(request, "Multiple users found with this email. Please contact support.")
            else:
                messages.error(request, "Invalid OTP or email.")

        # RESET PASSWORD STEP
        elif step == 'reset_password':
            password = request.POST.get('password')
            user_id = request.session.get('reset_user_id')

            try:
                user = User.objects.get(id=user_id)
                user.set_password(password)
                user.save()
                request.session.flush()
                messages.success(request, "Password reset successful.")
                return redirect('auth_view')
            except User.DoesNotExist:
                messages.error(request, "Something went wrong.")

    return render(request, 'forgot_password.html', {
        'step': request.session.get('step', 'login')
    })



# Shortcut to start password reset flow
def start_password_reset(request):
    request.session.flush()
    request.session['step'] = 'request_password_reset'
    return redirect('exporters_app:auth_view')
def verify_otp(request):
    if request.method == 'POST':
        code = request.POST.get('otp')
        user_id = request.session.get('pending_user_id')
        purpose = request.session.get('otp_purpose')  # 'register', '2fa', or 'reset'

        try:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.filter(user=user, code=code, purpose=purpose).latest('created_at')

            if otp.is_expired():
                messages.error(request, "OTP expired. Please request a new one.")
                return redirect('verify_otp')

            # Valid OTP
            if purpose == 'register' or purpose == '2fa':
                login(request, user)
                messages.success(request, "Verification successful. You are now logged in.")
                request.session.flush()
                return redirect('home')  # Replace with your home URL

            elif purpose == 'reset':
                request.session['reset_user_id'] = user.id
                request.session['step'] = 'reset_password'
                return redirect('exporters_app:auth_view')  # Leads to reset password form

        except (User.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')
def resend_otp(request):
    user_id = request.session.get('pending_user_id')
    purpose = request.session.get('otp_purpose')

    try:
        user = User.objects.get(id=user_id)
        otp_code = OTPService.generate()
        OTP.objects.create(
            user=user,
            code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        OTPService.send(user.email, otp_code)
        messages.success(request, "OTP resent successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('verify_otp')
def start_password_reset(request):
    request.session.flush()
    request.session['step'] = 'request_password_reset'
    return redirect('exporters_app:auth_view')  # or wherever your password reset logic is





# ------------------ M-Pesa Integration ------------------ #

