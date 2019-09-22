from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.urls import reverse 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime 
from rango.models import Category, Page 
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm 

def session_page(request):
	context_dict = {}

	if request.method == 'POST':
		username_form = request.POST['username_form']
		request.session['username_session'] = username_form 
		
		return redirect(reverse('rango:session_page'))


	# GET Method
	username_session = request.session.get('username_session')
	context_dict['username_session'] = username_session
	return render(request, 'rango/session_page.html', context_dict)

def cookie_page(request):
	''' 
	Has a page counter cookie and a form to obtain name from user
	via a cookie and to display it
	''' 
	context_dict = {}

	page_counter = int(request.COOKIES.get('cookie_page_counter', 1))
	context_dict['cookie_page_counter'] = page_counter 

	if request.method == 'POST':
		username_form = request.POST.get('username_form')
		username_form = username_form if username_form else 'default name'

		# Update context dict so you can display the information 
		context_dict['username_cookie'] = username_form
		
		# Create response object
		response = render(request, 'rango/cookie_page.html', context_dict)

		# Update the response object with the new cookie and send it back to the client
		response.set_cookie('username_cookie', username_form)
		return response

	# GET METHOD 
	username_cookie = request.COOKIES.get('username_cookie', 'no name')
	context_dict['username_cookie'] = username_cookie

	# Create response object
	response = render(request, 'rango/cookie_page.html', context_dict)
	
	# Update the response object with a cookie and send it back to the client
	page_counter += 1
	response.set_cookie('cookie_page_counter', str(page_counter))

	return response


def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val 
	return val 

def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request,
		'last_visit',
		str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],
		'%Y-%m-%d %H:%M:%S')
	if (datetime.now() - last_visit_time).seconds > 0:
		visits = visits + 1

		# Update the last visit cookie now that we have updated the count 
		request.session['last_visit'] = str(datetime.now()) 
	else:
		# Set the last visit cookie
		request.session['last_visit'] = last_visit_cookie 

	# Update/set the visits cookie
	request.session['visits'] = visits 

'''
def visitor_cookie_handler(request, response):
	# Get the number of visits to the site.
	# We use the COOKIES.get() function to obtain the visits cookie.
	# If the cookie exists, the value returned is casted to an integer.
	# If the cookie doesn't exist, then the default value of 1 is used.
	visits = int(request.COOKIES.get('visits', '1'))

	last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],
		'%Y-%m-%d %H:%M:%S')

	# If it's been more than a day since the last visit...
	if (datetime.now() - last_visit_time).seconds > 0:
		visits = visits + 1
		# Update the last visit cookie now that we have updated the count
		response.set_cookie('last_visit', str(datetime.now()))
	else:
		# Set the last visit cookie
		response.set_cookie('last_visit', last_visit_cookie)

	# update/set the visits cookie
	response.set_cookie('visits', visits)
'''

# TODO - downnload test_module.py and test your app
def index(request):
	# Query the database for a lost of ALL categories currently stored.
	# Order the categories by the number of likes in descending order.
	# Retrieve the top 5 only -- or all of less than 5.
	# Place the list in our context_dict dictionary (with our boldmessage!)
	# that will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
	context_dict = {}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] = category_list
	context_dict['pages'] = pages_list

	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	# Obtain our Response object early so we can add cookie information.
	response = render(request, 'rango/index.html', context_dict)

	
	# Return response back to the user, updating any cookies that need changed.
	return response 

def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict ={}

	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages.
		# Note tha tfilter() will return a list of page objects or an empty list
		pages = Page.objects.filter(category=category)

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages 
		# We also add the category object from
		# the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category 
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything -
		# the template will display the "no category" message for us.
		context_dict['category'] = None 
		context_dict['pages'] = None 

	# Go render the response and return it to the client.
	return render(request, 'rango/category.html', context_dict)


def add_category(request):
	form = CategoryForm()

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)
			# Now that the category is saved
			# We could give a confirmation message
			# But since the most recent category added is on the index page
			# Then we can redirect the user back to the index page.
			return index(request)
		else:
			# The supplied form contained errors -
			# just print them to the terminal.
			print('There are errors:')
			print(form.errors)

	# Will handle the bad form, new form, or no form supplied cases.
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form':form})


def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None 

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category 
				page.views = 0
				page.save()

				return redirect(reverse('rango:show_category',
					kwargs={'category_name_slug':
						category_name_slug}))
		else:
			print(form.errors)
	context_dict = {'form': form, 'category':category}
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	# A boolean value for telling the template
	# whether the registration was successful.
	# Set the False initially. Code changes value to
	# True when registration succeeds. 
	registered = False 

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		# @ creates a form object
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			# @ creates a model object
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile intance.
			# Since we need to set the user attribute ourselves,
			# we set the commit=False. This delays saving the model
			# until we're reade to avoid integrity problems.
			# @ UserProfile model needs user attribute to be set
			profile = profile_form.save(commit=False)
			profile.user = user 

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and
			# put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to indicate that the template
			# registration was successful.
			registered = True 
		else:
			# invalid form or forms - mistakes or something else?
			# print problems to the terminal
			print(user_form.errors, profile_form.errors)
	else:
		# Not a HTTP POST, so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user input.
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render(request,
		'rango/register.html',
		{'user_form': user_form,
		'profile_form': profile_form,
		'registered': registered})


def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
		# We use request.POST.get('<variable>') as opposed
		# to request.POST['<variable>'], because the,
		# request.POST.get['<variable>'] return None if the
		# value does not exist, while request.POST['<variable>']
		# will raise a KeyError exception.
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credential was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return redirect(reverse('rango:index'))
			else:
				# An inactive account was used - no logging in!
				return HttpResponse("Your Rango account is disabled.")
		else:
			# Bad login details were provided. So we can't log the user in.
			print("Invalid login details: {0} {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")

	# The request is not a HTTP POST, so display the login form.
	# This scenerio would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'rango/login.html')


@login_required
def user_logout(request):
	logout(request)
	return redirect(reverse('rango:index'))



def about(request):
	context_dict = {'your_name' :'Adam Janca'}
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	return render(request, 'rango/about.html', context=context_dict)