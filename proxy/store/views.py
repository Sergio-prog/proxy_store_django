from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .models import CustomUser, Payment, PaymentSides, Product


def index(request):
    all_proxies = Product.objects.all()
    print(all_proxies)
    return render(request, "index.html", {"proxies": all_proxies})


def signup(request):
    print(type(request))

    if request.method == "POST":
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
        #     user = form.save()
        #     login(request, user)
        #     return redirect('store/login.html')

        print(request.POST)

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
    all_credit_payments: list[Payment] = Payment.objects.filter(user_id=user_id, side="Credit")
    all_debit_payments: list[Payment] = Payment.objects.filter(user_id=user_id, side="Debit")

    deposit = 0
    withdraw = 0

    for payment in all_credit_payments:
        deposit += payment.amount

    for payment in all_debit_payments:
        withdraw += payment.amount

    balance = deposit - withdraw
    return balance


def deposit(request):
    if request.method == "POST":
        amount = request.POST["amount"]
        user_id = request.POST["to"]

        print(request.user)

        Payment(side=PaymentSides.Credit, amount=amount, user_id=user_id).save()
        recalculate_balance(user_id)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
