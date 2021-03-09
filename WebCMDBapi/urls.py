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
	path('api/search/generic/all/', views.AllSearchGeneric.as_view(), name='all_search_generic'),
]