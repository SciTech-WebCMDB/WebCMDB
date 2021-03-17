from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes

from .serializers import ComputerSerializer, ServerSerializer, SearchSerializer
from .models import Computer, Server
from .tasks import import_csv_computer_task

from drf_haystack.generics import HaystackGenericAPIView
from haystack.query import SearchQuerySet
from django.http import JsonResponse

import uuid, re, csv
from io import TextIOWrapper
from django.core.management import call_command

# from celery import shared_task
# from celery_progress.backend import ProgressRecorder

# Create your views here.

def index(request):
	return render(request, 'WebCMDBapi/index.html')

class AllSearchGeneric(HaystackGenericAPIView):
	# source: DRF Haystack documentation
	# My old Eenna/WebCMDB
	# Add this to fix Query doesnt look up for 2 modes: HAYSTACK_LIMIT_TO_REGISTERED_MODELS = False
	serializer_class = ServerSerializer
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

	def get_queryset(self, *args, **kwargs):
		queryset = SearchQuerySet().all().filter(content=self.request.GET.get('search'))
		return queryset

	def get(self, request):
		query_param = self.request.GET.get('search')
		queryset = self.get_queryset() 
		print(queryset)

		content = []
		for x in queryset:
			if str(x.object._meta) == 'WebCMDBapi.computer':
				content.append(ComputerSerializer(instance=x.object).data)
			elif str(x.object._meta) == 'WebCMDBapi.server':
				content.append(ServerSerializer(instance=x.object).data)

		# Regex for UUID, need len >= 6
		# TODO: auto redirect to the detail page?
		uuid_pattern = re.compile("[0-9a-fA-F-.\d]+")
		if len(query_param) >= 6 and uuid_pattern.search("query_param"):
			if Computer.objects.filter(id__contains=query_param).exists():
				content.extend(list(ComputerSerializer(Computer.objects.filter(id__contains=query_param), many=True).data))
			if Server.objects.filter(id__contains=query_param).exists():
				content.extend(list(ServerSerializer(Computer.objects.filter(id__contains=query_param), many=True).data))

		if self.request.path_info.startswith('/api/'):
			return JsonResponse(content, safe=False)
		#return HTML here

class ComputerSearchGeneric(generics.ListAPIView):
	# cdrf.co/3.1/rest_framework.generics/ListAPIView.html
	model = Computer
	queryset = Computer.objects.all()
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computers.html'
	filter_backends = [filters.SearchFilter]
	search_fields = ['hostname', 'location', 'ipv4']

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())
		if self.request.path_info.startswith('/api/'):
			return JsonResponse((ComputerSerializer(queryset, many=True)).data, safe=False)
		return Response({'computers':queryset})

class ServerSearchGeneric(generics.ListAPIView):
	# cdrf.co/3.1/rest_framework.generics/ListAPIView.html
	model = Server
	queryset = Server.objects.all()
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/servers.html'
	filter_backends = [filters.SearchFilter]
	search_fields = ['servername', 'location', 'ipv4']

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())
		if self.request.path_info.startswith('/api/'):
			return JsonResponse((ServerSerializer(queryset, many=True)).data, safe=False)
		return Response({'servers':queryset})

#----------------------------------------------------------------------------
# Show all computers/servers

class ComputerAPIView(generics.ListAPIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computers.html'
	model = Computer

	def get(self, request):
		queryset = Computer.objects.all()
		serializer_class = ComputerSerializer
		return Response({'computers':queryset})

class ServerAPIView(generics.ListAPIView):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'WebCMDBapi/servers.html'
	model = Server

	def get(self, request):
		queryset = Server.objects.all().order_by('servername')
		serializer_class = ServerSerializer
		return Response({'servers':queryset})

#----------------------------------------------------------------------------
# Computer/Server Detail

class ComputerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/computer_detail.html'
	model = Computer

	def get(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			computer = get_object_or_404(Computer, pk=pk)
			serializer = ComputerSerializer(computer)
			if self.request.path_info.startswith('/api/'):
				return JsonResponse(serializer.data)
			return Response({'serializer': serializer, 'computer': computer})
		else:
			serializer = ComputerSerializer()
			return Response({'serializer': serializer})

	def post(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			computer = get_object_or_404(Computer, pk=pk)
			serializer = ComputerSerializer(computer, data=request.data)
			if not serializer.is_valid():
				return Response({'serializer': serializer, 'computer': computer})
			serializer.save()
			return redirect('WebCMDBapi:computers')
		else:
			serializer = ComputerSerializer(data=request.data)
			if serializer.is_valid():
				computer = serializer.save()
				return redirect('WebCMDBapi:computer_detail', pk=computer.pk)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerDetailAPIView(APIView):
	renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
	template_name = 'WebCMDBapi/server_detail.html'
	model = Server

	def get(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			server = get_object_or_404(Server, pk=pk)
			serializer = ServerSerializer(server)
			if self.request.path_info.startswith('/api/'):
				return JsonResponse(serializer.data)
			return Response({'serializer': serializer, 'server': server})
		else:
			serializer = ServerSerializer()
			return Response({'serializer': serializer})

	def post(self, request, pk):
		if pk != uuid.UUID('00000000000000000000000000000000'):
			server = get_object_or_404(Server, pk=pk)
			serializer = ServerSerializer(server, data=request.data)
			if not serializer.is_valid():
				return Response({'serializer': serializer, 'server': server})
			serializer.save()
			return redirect('WebCMDBapi:servers')
		else:
			serializer = ServerSerializer(data=request.data)
			if serializer.is_valid():
				server = serializer.save()
				return redirect('WebCMDBapi:server_detail', pk=server.pk)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def delete(request, pk):
	if 'computer' in request.path_info:
		computer = get_object_or_404(Computer, pk=pk)
		computer.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	elif 'server' in request.path_info:
		server = get_object_or_404(Server, pk=pk)
		server.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

def upload(request):
	template = "upload.html"
	if request.method == 'GET':
		return render(request, template, {})

def import_csv_computer(request):
	if request.method == 'POST':
		csv_file = TextIOWrapper(request.FILES['file'].file, encoding=request.encoding)
		data = list(csv.reader(csv_file))
		if 'overwrite' in request.POST:
			data.append(True)
		else:
			data.append(False)
		result = import_csv_computer_task.delay(data)
		call_command('update_index')
		return render(request, 'WebCMDBapi/display_progress.html', context={'task_id': result.task_id})














#-------------------------------------------------------------------------------------------#
#                         THIS DOESNT USE CELERY - FOR BACKUP ONLY                          #
#-------------------------------------------------------------------------------------------#
# def import_csv_computer(request):
# 	# You try to get the machine, if exists, update
# 	# Else create.
# 	# AKA Overwrite
# 	template = 'upload.html'
# 	if request.method == 'GET':
# 		return render(request, template, {})
# 	elif request.method == 'POST':
# 		csv_file = TextIOWrapper(request.FILES['file'].file, encoding=request.encoding)
# 		data = csv.reader(csv_file)
# 		for row in data:
# 			if str(row[0]) == '':
# 				# I do not deal with empty hostname computer right now.
# 				pass
# 			else:
# 				computer, created = Computer.objects.get_or_create(
# 					hostname = str(row[0]),
# 				)
# 				if 'overwrite' in request.POST:
# 					computer.location = str(row[1])
# 					computer.ipv4 = str(row[2])
# 					computer.ipv6 = str(row[3])
# 					computer.os = str(row[4])
# 					computer.physical_virtual = str(row[5])
# 					computer.owner = str(row[6])
# 					computer.administrator = str(row[7])
# 					computer.uofa_tag_number = str(row[8])
# 					computer.make_model = str(row[9])
# 					computer.cpu = str(row[10])
# 					computer.ram = str(row[11])
# 					computer.storage = str(row[12])
# 					computer.gpu = str(row[13])
# 					computer.serial_number = str(row[14])
# 					computer.status = str(row[15]).upper()
# 					computer.rack = str(row[16]),
# 					computer.scitech_access = str(row[17])
# 					computer.power_up_priority = str(row[18])
# 					computer.support_team = str(row[19])
# 					computer.department = str(row[20])
# 					computer.comments = str(row[21])
			
# 				computer.save()
# 		return redirect('WebCMDBapi:computers')

