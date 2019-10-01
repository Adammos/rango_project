from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.urls import reverse 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 

from datetime import datetime 
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm 
from rango.bing_search import run_query
from django.views import View 
from django.utils.decorators import method_decorator


class SearchAddPageView(View):
	@method_decorator(login_required)
	def get(self, request):
		category_id = request.GET['category_id']
		page_title = request.GET['page_id']
		page_url = request.GET['page_url']

		# test uknown 
		#page_test = request.GET['data-page-test']

		# Check whether category exitst
		try:
			category = Category.objects.get(id=int(category_id))
		except Category.DoesNotExist:
			return HttpResponse('Error - category not found.')
		except ValueError:
			return HttpResponse('Error - bad category ID.')

		# Add the page to category if it does not exist yet
		page = Page.objects.get_or_create(category=category, title=page_title, url=page_url)
			
		pages = Page.objects.filter(category=category).order_by('-views')	
		return render(request, 'rango/page_listing.html', {'pages':pages})



def get_category_list(max_results=0, starts_with=''):
	category_list = []

	if starts_with:
		category_list = Category.objects.filter(name__istartswith=starts_with)

	if max_results > 0:
		if len(category_list) > max_results:
			category_list = category_list[:max_results]

	return category_list 


class CategorySuggestionView(View):
	def get(self, request):
		suggestion = request.GET['suggestion']
		category_list = get_category_list(max_results=8, starts_with=suggestion)

		if len(category_list) == 0:
			category_list = Category.objects.order_by('-likes')

		return render(request, 'rango/categories.html', {'categories': category_list})

class LikeCategoryView(View):
	@method_decorator(login_required)
	def get(self, request):
		category_id = request.GET['category_id']

		try:
			category = Category.objects.get(id=int(category_id))
		except Category.DoesNotExist:
			return HttpResponse(-1)
		except ValueError:
			return HttpResponse(-1)

		category.likes = category.likes + 1
		category.save()

		return HttpResponse(category.likes)

class ListProfilesView(View):
	@method_decorator(login_required)
	def get(self, request):
		profiles = UserProfile.objects.all()

		return render(request, 'rango/list_profiles.html', {'userprofile_list': profiles})

class ProfileView(View):
	def get_user_details(self, username):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			# this will raise TypeError in the calling method
			return None

		userprofile = UserProfile.objects.get_or_create(user=user)[0]
		form = UserProfileForm({'website': userprofile.website,
								'picture': userprofile.picture})
		return (user, userprofile, form)

	@method_decorator(login_required)
	def get(self, request, username):
		try:
			(user, userprofile, form) = self.get_user_details(username)
		except TypeError:
			return redirect('rango:index')

		context_dict = {'userprofile': userprofile,
						'selecteduser': user,
						'form': form}
		return render(request, 'rango/profile.html', context_dict)

	@method_decorator(login_required)
	def post(self, request, username):
		try:
			(user, userprofile, form) = self.get_user_details(username)
		except TypeError:
			return redirect('rango:index')
		
		# Users can change only their own profiles
		if request.user != user:
			return redirect('rango:index')

		form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

		if form.is_valid():
			form.save(commit=True)
			return redirect('rango:profile', user.username)
		else:
			print(form.errors)

		context_dict = {'userprofile': userprofile,
						'selecteduser': user,
						'form': form}
		return render(request, 'rango/profile.html', context_dict)
'''
def about(request):
	context_dict = {'your_name' :'Adam Janca'}
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	return render(request, 'rango/about.html', context=context_dict)
'''

class AboutView(View):
	def get(self, request):
		context_dict = {}
		context_dict['visits'] = request.session['visits']
		return render(request, 'rango/about.html', context_dict)

'''
@login_required
def register_profile(request):
	form = UserProfileForm()

	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES)

		if form.is_valid():
			user_profile = form.save(commit=False)
			user_profile.user = request.user 
			user_profile.save()

			return redirect('rango:index')
		else:
			print(form.errors)
	context_dict = {'form': form}
	return render(request, 'rango/profile_registration.html', context_dict)
'''
class RegisterProfileView(View):
	@method_decorator(login_required)
	def post(self, request):
		form = UserProfileForm(request.POST, request.FILES)
		if form.is_valid():
			user_profile = form.save(commit=False)
			user_profile.user = request.user
			user_profile.save()
			return redirect('rango:index')
		else:
			print(form.errors)
			context_dict = {'form': form}
			return render(request, 'rango/profile_registration.html', context_dict)

	@method_decorator(login_required)
	def get(self, request):
		form = UserProfileForm()
		context_dict = {'form': form}
		return render(request, 'rango/profile_registration.html', context_dict)

'''
def goto_url(request):
	page_id = None
	if request.method == 'GET':
		page_id = request.GET.get('page_id')
		if not page_id:
			return redirect(reverse('rango:index'))

		try:
			page = Page.objects.get(id=page_id)
		except Page.DoesNotExist:
			return redirect(reverse('rango:index'))

		page.views += 1
		page.save()
		return redirect(page.url)
	
	return redirect(reverse('rango:index'))
'''

class GoToView(View):
	def get(self, request):
		page_id = request.GET.get('page_id')
		if not page_id:
			return redirect(reverse('rango:index'))

		try:
			page = Page.objects.get(id=page_id)
		except Page.DoesNotExist:
			return redirect(reverse('rango:index'))

		page.views += 1
		page.save()
		return redirect(page.url)
	
	def post(self, request):
		return redirect(reverse('rango:index'))	

'''
def search(request):
	result_list = []
	query = ''
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Bing function to get the results list!
			result_list = run_query(query)

	return render(request, 'rango/search.html', {'result_list': result_list, 'query_string':query})
'''

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
'''
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
'''
class IndexView(View):
	def get(self, request):
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
'''
def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict ={}
	
	# Search functionality
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Bing function to get the results list!
			result_list = run_query(query)
			context_dict['result_list'] = result_list
			context_dict['query_string'] = query
	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages.
		# Note tha tfilter() will return a list of page objects or an empty list
		pages = Page.objects.filter(category=category).order_by('-views')

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
'''

class ShowCategoryView(View):
	def get_context_dict(self, category_name_slug):
		context_dict = {'category': None, 'pages': None}
		try:
			category = Category.objects.get(slug=category_name_slug)
			pages = Page.objects.filter(category=category).order_by('-views')
			context_dict['category'] = category
			context_dict['pages'] = pages 
		except Category.DoesNotExist:
			pass
		return context_dict

	def get(self, request, category_name_slug):
		context_dict = self.get_context_dict(category_name_slug)
		return render(request, 'rango/category.html', context_dict)

	def post(self, request, category_name_slug):
		context_dict = self.get_context_dict(category_name_slug)
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
			context_dict['result_list'] = result_list
			context_dict['query_string'] = query
		return render(request, 'rango/category.html', context_dict)

'''
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
'''

class AddCategoryView(View):
	@method_decorator(login_required)
	def get(self, request):
		form = CategoryForm()
		return render(request, 'rango/add_category.html', {'form': form})

	@method_decorator(login_required)
	def post(self, request):
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return redirect(reverse('rango:index'))
		else:
			print(form.errors)
		return render(request, 'rango/add_category.html', {'form': form})

'''
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
'''
class AddPageView(View):
	def get_category(self, category_name_slug):
		try:
			category = Category.objects.get(slug=category_name_slug)
		except Category.DoesNotExist:
			category = None
		return category 

	def get(self, request, category_name_slug):
		category = self.get_category(category_name_slug)
		form = PageForm()
		context_dict = {'form': form, 'category': category}
		return render(request, 'rango/add_page.html', context_dict)

	def post(self, request, category_name_slug):
		category = self.get_category(category_name_slug)
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()

				return redirect(reverse('rango:show_category', 
					kwargs={'category_name_slug': category_name_slug}))
		else:
			print(form.errors)
		context_dict = {'form': form, 'category': category}
		return render(request, 'rango/add_page.html', context_dict)

'''
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
'''

'''
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
'''
'''
@login_required
def user_logout(request):
	logout(request)
	return redirect(reverse('rango:index'))
'''
