from django.shortcuts import render
from basic.forms import UserForm,UserProfileInfoForm
from basic.models import UserProfileInfo
from django.conf import settings
from basic.utils import writeTofile , convertToBinaryData


# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import os





def index(request,context=None):

    imagefile=None
    if request.user.is_authenticated and context == None:
        profile = UserProfileInfo.objects.get(user=request.user)
        if profile.blob != None:
            blob = profile.blob
            file_path = str(settings.BASE_DIR)+"/media/"+"photos/temp.png"
            writeTofile(blob,file_path)
            profile.profile_pic = "photos/temp.png"
            imagefile= profile.profile_pic


        name=profile.name
        context = {'imagefile': imagefile,'name': name}


    return render(request,'basic/index.html',context)



@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))


@login_required
def update(request):
    # Log out the user.
    # Return to homepage.
    updated=False
    if request.method == 'POST':
        profile_form = UserProfileInfoForm(data=request.POST)
        if profile_form.is_valid():

            profile = profile_form.save(commit=False)
            saved_prof = UserProfileInfo.objects.get(user=request.user)
            if 'profile_pic' in request.FILES:
                # print("found*****",profile.profile_pic)
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']

            saved_prof.profile_pic=profile.profile_pic
            saved_prof.name= profile.name
            saved_prof.save()

            ## Save to blob
            file_path=None
            if 'profile_pic' in request.FILES:
                file_path = str(settings.BASE_DIR)+"/media/"+str(saved_prof.profile_pic)
                # print(file_path)
                blob = convertToBinaryData(file_path)
            else:
                blob=None

            saved_prof.profile_pic=profile.profile_pic
            saved_prof.blob= blob
            saved_prof.save()

            if file_path and os.path.exists(file_path):
              os.remove(file_path)
            else:
              print("The file does not exist")

            updated = True
        else:
            print(profile_form.errors)
    else:
        profile_form = UserProfileInfoForm()

    return render(request,'basic/update.html',
                          {
                           'profile_form':profile_form,
                           'updated':updated})








def register(request):

    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)


        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!

            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)

            profile.user = user

            # Check if a profile picture is provided
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']
            #  save model
            profile.save()
            file_path=None
            if 'profile_pic' in request.FILES:
                file_path = str(settings.BASE_DIR)+"/media/"+str(profile.profile_pic)
                print(file_path)
                blob = convertToBinaryData(file_path)
                # print(blob)
                profile.blob= blob
                # profile.profile_pic= 'photos/temp.png'
                profile.save()

                if file_path and os.path.exists(file_path):
                  os.remove(file_path)
                else:
                  print("The file does not exist")


            # Registration Successful!
            registered = True
            login(request,user)
            return HttpResponseRedirect('/')


        else:
            print(user_form.errors,profile_form.errors)

    else:
        # If not a POST request

        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request,'basic/registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            if user.is_active:
                # Log the user in.
                login(request,user)

                profile = UserProfileInfo.objects.get(user=user)
                if profile.blob != None:
                    blob = profile.blob
                    file_path = str(settings.BASE_DIR)+"/media/"+"photos/temp.png"
                    writeTofile(blob,file_path)
                    profile.profile_pic = "photos/temp.png"




                imagefile= profile.profile_pic
                print(imagefile)

                ## Send user to home page
                context = {'imagefile': imagefile,'name': profile.name}
                response = index(request, context)
                return response
            else:
                # If account is not active
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

    else:
        #Nothing has been provided for username or password.
        return render(request, 'basic/login.html', {})
