from django.urls import include, path
from django.conf.urls import url
from . import views

app_name = 'WebCMDBapi'

urlpatterns = [
	path('', views.index, name='index'),
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('computers/', views.ComputerAPIView.as_view(), name='computers'),
	path('servers/', views.ServerAPIView.as_view(), name='servers'),
	path('computer_detail/<uuid:pk>/', views.ComputerDetailAPIView.as_view(), name='computer_detail'),
	path('server_detail/<uuid:pk>/', views.ServerDetailAPIView.as_view(), name='server_detail'),
	path('api/computer_detail/<uuid:pk>/', views.ComputerDetailAPIView.as_view(), name='computer_detail_json'),
	path('api/server_detail/<uuid:pk>/', views.ServerDetailAPIView.as_view(), name='server_detail_json'),
	path('search/generic/computer/', views.ComputerSearchGeneric.as_view(), name='computer_search_generic'),
	path('search/generic/server/', views.ServerSearchGeneric.as_view(), name='server_search_generic'),
	path('search/generic/all/', views.AllSearchGeneric.as_view(), name='all_search_generic'),
	path('api/search/generic/all/', views.AllSearchGeneric.as_view(), name='all_search_generic_api'),
	path('api/search/generic/computer/', views.ComputerSearchGeneric.as_view(), name='computer_search_generic_api'),
	path('api/search/generic/server/', views.ServerSearchGeneric.as_view(), name='server_search_generic_api'),
	path('api/computer_detail/<uuid:pk>/delete/', views.delete, name='computer_delete_api'),
	path('api/server_detail/<uuid:pk>/delete/', views.delete, name='server_delete_api'),
	path('computer_detail/<uuid:pk>/delete/', views.delete, name='computer_delete'),
	path('server_detail/<uuid:pk>/delete/', views.delete, name='server_delete'),
	path('upload/', views.upload, name='upload'),
	path('progress/', views.import_csv_computer, name='import_csv_computer'),
	path('api/diff', views.diff, name='diff'),
	path('update_database/', views.update_database, name='update_database'),
]