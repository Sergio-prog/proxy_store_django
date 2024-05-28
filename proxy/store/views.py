from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .models import CustomUser, Payment, PaymentSides, Product, InsufficientBalance


def index(request):
    all_proxies = Product.objects.all()
    return render(request, "index.html", {"proxies": all_proxies})


def signup(request):
    print(type(request))

    if request.method == "POST":
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
        #     user = form.save()
        #     login(request, user)
        #     return redirect('store/login.html')

        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        hashed_password = make_password(password)

        CustomUser.objects.create_user(username, email, hashed_password)

        return redirect(reverse('store:signin'))

    return render(request, 'store/register.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        print(username, password)

        hashed_password = make_password(password)

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is None:
            error_message = "User was not authenticated. Maybe invalid password or username."
            return render(request, "store/login.html", {"error_message": error_message})

        login(request, user)
        return HttpResponse(user)

    return render(request, 'store/login.html')


def recalculate_balance(user_id: str) -> int:
    user = CustomUser.objects.get(pk=user_id)

    all_credit_payments: list[Payment] = Payment.objects.filter(user_id=user_id, side="Credit")
    all_debit_payments: list[Payment] = Payment.objects.filter(user_id=user_id, side="Debit")

    deposit = 0
    withdraw = 0

    for payment in all_credit_payments:
        deposit += payment.amount

    for payment in all_debit_payments:
        withdraw += payment.amount

    balance = deposit - withdraw

    if balance < 0:
        raise InsufficientBalance(balance)

    user.balance = balance
    user.save()

    return balance


def deposit(request):
    if request.method == "POST":
        amount = request.POST["amount"]
        user_id = request.POST["to"]

        print(request.user)

        Payment(side=PaymentSides.Credit, amount=amount, user_id=user_id).save()
        recalculate_balance(user_id)


def detail_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExit:
        raise Http404("Product not found")

    return render(request, "store/products/detail.html", {"product": product})


@login_required(login_url="/accounts/login/")
def buy_product(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id)
        user = request.user
        price = product.price

        if not request.user.check_balance(price):
            messages.error(request, f"Insufficient Balance. Needs at least {price}$")

            return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))

        buy_payment = Payment(side=PaymentSides.Debit, amount=price, user_id=user.id)

        product.in_stock -= 1
        product.save()

        buy_payment.save()

        recalculate_balance(user.id)

        messages.success(request, f"Successfully purchased one proxy.")
        return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))
    else:
        return HttpResponse(status=405)


@login_required(login_url="/accounts/login/")
def profile(request):
    return render(request, "store/profile.html")


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
