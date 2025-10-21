from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Category, User
from .forms import UserSignupForm, UserLoginForm, ProductForm, EditProfileForm, CategoryForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings


# home page
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def product(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products.html', {'products': products, 'categories': categories})

# Landing page for buyer or unregistered user
def buyer_home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'buyer_home.html', {'products': products, 'categories': categories})


# Signup page
def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)

                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_HOSTS):
                    return redirect(next_url)

                if user.role == 'seller':
                    return redirect('seller_home')
                return redirect('buyer_home')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required
@login_required
def seller_home(request):
    if request.user.role != 'seller':
        return redirect('buyer_home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_home')
    else:
        form = ProductForm()

    my_products = Product.objects.filter(seller=request.user)

    # Pass the logged-in user's profile for navbar
    return render(request, 'seller_home.html', {
        'form': form,
        'my_products': my_products,
        'user_profile': request.user
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_home')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('seller_home')
    return render(request, 'confirm_delete.html', {'product': product})


def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_products = Product.objects.filter(seller=user) if user.role == 'seller' else []
    is_owner = request.user.is_authenticated and request.user.pk == user.pk
    return render(request, 'profile.html', {
        'user_profile': user,
        'products': user_products,
        'is_owner': is_owner
    })


@login_required
def edit_profile(request, pk):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile = form.save(commit=False)

            new_password = form.cleaned_data.get('new_password')
            if new_password:
                profile.set_password(new_password)

            if profile.security_answer_1 and profile.security_answer_2:
                profile.profile_completed = True

            profile.save()
            return redirect('profile', pk=user.pk)
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})


def forget_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            request.session['reset_user_id'] = user.id
            return redirect('forget_password_verify')
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
    return render(request, 'forget_password_request.html')


def forget_password_verify(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forget_password_request')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')
        if answer1 == user.security_answer_1 and answer2 == user.security_answer_2:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully.')
                del request.session['reset_user_id']
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'Incorrect answers.')
    return render(request, 'forget_password_verify.html', {'user': user})


# ---------------- ADMIN DASHBOARD ----------------
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    users = User.objects.all()
    products = Product.objects.all()
    categories = Category.objects.all()

    # User filters
    role_filter = request.GET.get("role")
    if role_filter in ["buyer", "seller"]:
        users = users.filter(role=role_filter)

    user_email_filter = request.GET.get("user_email")
    if user_email_filter:
        users = users.filter(email__icontains=user_email_filter)

    # Product filters
    category_filter = request.GET.get("category")
    if category_filter:
        products = products.filter(category_id=category_filter)

    seller_email_filter = request.GET.get("seller_email")
    if seller_email_filter:
        products = products.filter(seller__email__icontains=seller_email_filter)

    # Add new category
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CategoryForm()

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'products': products,
        'categories': categories,
        'form': form,
        'role_filter': role_filter,
        'user_email_filter': user_email_filter,
        'category_filter': category_filter,
        'seller_email_filter': seller_email_filter,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_entry(request, model, pk):
    model_map = {
        "user": User,
        "product": Product,
        "category": Category,
    }

    Model = model_map.get(model.lower())
    if not Model:
        return redirect('admin_dashboard')

    obj = get_object_or_404(Model, pk=pk)
    obj.delete()
    return redirect('admin_dashboard')


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    error = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or not authorized as admin."

    return render(request, 'admin_login.html', {'error': error})
