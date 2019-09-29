from django.urls import path
from rango import views
 

app_name = 'rango'

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'),
	path('about/', views.AboutView.as_view(), name='about'),
	path('category/<slug:category_name_slug>/',
		views.ShowCategoryView.as_view(), name='show_category'),
	path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
	path('<slug:category_name_slug>/add_page/', 
		views.AddPageView.as_view(), name='add_page'),
	path('cookie_page/', views.cookie_page, name='cookie_page'),
	path('session_page/', views.session_page, name='session_page'),
	path('goto/', views.GoToView.as_view(), name='goto'),
	path('register_profile/', views.RegisterProfileView.as_view(), name='register_profile'),
	path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
	path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
	path('like_category/', views.LikeCategoryView.as_view(), name='like_category'),
]