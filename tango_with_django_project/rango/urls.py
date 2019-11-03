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
	path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),
	path('search_add_page/', views.SearchAddPageView.as_view(), name='search_add_page'),
	path('guess_number_game/', views.GuessNumberView.as_view(), name='guess_number_game'),
	path('random_tiles/', views.RandomTiles.as_view(), name='random_tiles'),
	path('bouncing_balls/', views.BouncingBallsView.as_view(), name='bouncing_balls'),
	path('comments', views.CommentsView.as_view(), name='comments'),
]