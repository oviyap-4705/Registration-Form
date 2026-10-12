from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import RegistrationSerializer
from .models import Registration
from django.views.decorators.http import require_http_methods


def home(request):

    return render(
        request,
        "home.html"
    )


def register_page(request):

    return render(
        request,
        "registration/register.html"
    )


def login_page(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        
        try:

            registration = Registration.objects.get(
                email=email
            )

        except Registration.DoesNotExist:

            return render(
                request,
                "registration/login.html",
                {
                    "error": "Invalid email or password."
                }
            )

        if not check_password(password, registration.password):

            return render(
                request,
                "registration/login.html",
                {
                    "error": "Invalid email or password."
                }
            )

       
        request.session["registration_id"] = (
            registration.id
        )

        return redirect("/profile/")


    return render(
        request,
        "registration/login.html"
    )


def profile_page(request):

    # Get logged-in user's ID
    registration_id = request.session.get(
        "registration_id"
    )

    # User is not logged in
    if not registration_id:

        return redirect("/login/")


    # Find registered user
    try:

        registration = Registration.objects.get(
            id=registration_id
        )

    except Registration.DoesNotExist:

        request.session.flush()

        return redirect("/login/")



    if request.method == "POST":

        update_data = request.POST.copy()

        for field_name, uploaded_file in request.FILES.items():

            update_data[field_name] = uploaded_file


        password = request.POST.get(
            "password",
            ""
        ).strip()

        if password == "":

            update_data.pop(
                "password",
                None
            )


        serializer = RegistrationSerializer(
            registration,
            data=update_data,
            partial=True
        )


        if serializer.is_valid():

            serializer.save()

            # Refresh object from database
            registration.refresh_from_db()

            return render(
                request,
                "registration/profile.html",
                {
                    "registration": registration,
                    "success": "Details updated successfully."
                }
            )

        return render(
            request,
            "registration/profile.html",
            {
                "registration": registration,
                "errors": serializer.errors
            }
        )


    return render(
        request,
        "registration/profile.html",
        {
            "registration": registration
        }
    )

def logout_page(request):

    request.session.flush()

    return redirect("/")



@api_view(['GET', 'POST'])
@parser_classes([
    MultiPartParser,
    FormParser
])
def registration_api(request):

    if request.method == 'GET':

        registrations = Registration.objects.all()

        serializer = RegistrationSerializer(
            registrations,
            many=True
        )

        return Response(
            serializer.data
        )


    if request.method == 'POST':

        serializer = RegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "message": "Registration successful",
                "data": serializer.data
            })


        print(
            "SERIALIZER ERRORS:",
            serializer.errors
        )

        return Response(
            serializer.errors,
            status=400
        )



@api_view([
    'GET',
    'PATCH',
    'DELETE'
])
@parser_classes([
    MultiPartParser,
    FormParser
])
def registration_detail_api(request, id):

    
    try:

        registration = Registration.objects.get(
            id=id
        )

    except Registration.DoesNotExist:

        return Response({
            "error": "Registration not found"
        }, status=404)



    if request.method == 'GET':

        serializer = RegistrationSerializer(
            registration
        )

        return Response(
            serializer.data
        )


    if request.method == 'PATCH':

        serializer = RegistrationSerializer(
            registration,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "message": "Registration updated successfully",
                "data": serializer.data
            })


        print(
            "SERIALIZER ERRORS:",
            serializer.errors
        )

        return Response(
            serializer.errors,
            status=400
        )


    if request.method == 'DELETE':

        registration.delete()

        return Response({
            "message": "Registration deleted successfully"
        })