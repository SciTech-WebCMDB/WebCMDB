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
from django.http import JsonResponse, HttpResponse

import uuid, re, csv, os
from io import TextIOWrapper
from subprocess import Popen, PIPE, STDOUT
from csv_diff import load_csv, compare

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
	template_name = 'WebCMDBapi/search_generic.html'

	def get_queryset(self, *args, **kwargs):
		queryset = SearchQuerySet().all().filter(content=self.request.GET.get('search'))
		return queryset

	def get(self, request):
		query_param = self.request.GET.get('search')
		queryset = list(self.get_queryset())

		# Regex for UUID, need len >= 6
		# TODO: auto redirect to the detail page?
		uuid_pattern = re.compile("[0-9a-fA-F-.\d]+")
		uuid_list = []
		if len(query_param) >= 6 and uuid_pattern.search("query_param"):
			computer_queryset = Computer.objects.filter(id__contains=query_param)
			if computer_queryset.count() > 0:
				for computer in computer_queryset:
					computer_id = str(computer.id)
					uuid_list.append({'type': 'computer', 'id': computer_id, 'url': f"/computer_detail/{computer_id}/"})
			server_queryset = Server.objects.filter(id__contains=query_param)			
			if server_queryset.count() > 0:
				for server in server_queryset:
					uuid_list.append({'type': 'server', 'id': str(server.id)})

		if len(uuid_list) == 1 and len(queryset) == 0:
			return redirect(uuid_list[0]['url'])
		elif len(uuid_list) == 0 and len(queryset) == 1:
			machine = queryset[0]
			if machine.model_name == "computer":
				return redirect(f"/computer_detail/{str(machine.object.id)}/")
			elif machine.model_name == "server":
				return redirect(f"/server_detail/{str(machine.object.id)}/")
		elif len(uuid_list) == 0 and len(queryset) == 0:
			return Response({"message": "no machine found."}, status=status.HTTP_404_NOT_FOUND)
	
		if self.request.path_info.startswith('/api/'):
			content = []
			for x in queryset:
				if x.model_name == "computer":
					content.append(
						{
							"type": "computer",
							"detail": ComputerSerializer(instance=x.object).data,
						}
					)
				elif x.model_name == "server":
					content.append(
						{
							"type": "server",
							"detail": ServerSerializer(instance=x.object).data,
						}
					)
			return JsonResponse(content, safe=False)
		else:
			return Response({'machines': queryset, 'uuid_list': uuid_list})
		#return HTML render here

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
			call_command('update_index', '--remove')
			return redirect('WebCMDBapi:computers')
		else:
			serializer = ComputerSerializer(data=request.data)
			if serializer.is_valid():
				computer = serializer.save()
				call_command('update_index', '--remove')
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
			call_command('update_index', '--remove')
			return redirect('WebCMDBapi:servers')
		else:
			serializer = ServerSerializer(data=request.data)
			if serializer.is_valid():
				server = serializer.save()
				call_command('update_index', '--remove')
				return redirect('WebCMDBapi:server_detail', pk=server.pk)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def delete(request, pk):
	if 'computer' in request.path_info:
		computer = get_object_or_404(Computer, pk=pk)
		computer.delete()
		call_command('update_index', '--remove')
		return Response(status=status.HTTP_204_NO_CONTENT)
	elif 'server' in request.path_info:
		server = get_object_or_404(Server, pk=pk)
		server.delete()
		call_command('update_index', '--remove')
		return Response(status=status.HTTP_204_NO_CONTENT)

def upload(request):
	template = "upload.html"
	if request.method == 'GET':
		return render(request, template, {})

def import_csv_computer(request):
	if request.method == 'POST':
		csv_file = TextIOWrapper(request.FILES['file'].file, encoding=request.encoding)
		data = list(csv.reader(csv_file, delimiter="|"))
		if 'overwrite' in request.POST:
			overwrite = True
		else:
			overwrite = False
		result = import_csv_computer_task.delay(data, overwrite)
		return render(request, 'WebCMDBapi/display_progress.html', context={'task_id': result.task_id})

def diff(request):
	if request.method == "GET":
		command = ["bash", "WebCMDBapi/bash/gitfetch.sh"]
		try:
			process = Popen(command, stdout=PIPE, stderr=STDOUT)
			output = process.stdout.read()
			exitstatus = process.poll()
			if (exitstatus==0):
				database_to_csv()
				diff = compare(
					load_csv(open("WebCMDBapi/data/machines/machines.csv"), key="21 UUID"),
					load_csv(open("WebCMDBapi/bash/machines/machines_tri.csv"), key="21 UUID")
				)
				result = {"status": "Success", "output":str(output)}
			else:
				diff = {"status":"Failed", "summary": "Failed"}
				result = {"status": "Failed", "output":str(output)}

		except Exception as e:
				diff = {"status":"Failed", "summary": "Failed"}
				result =  {"status": "failed", "output":str(e)}

		json_data = {
			"script": {
				"status": result["status"],
				"ouput": result["output"],
			},
			"summary": diff["summary"],
			"diff": diff,
		}

		return JsonResponse(json_data, safe=False)

def database_to_csv():
	machines = Computer.objects.all()
	with open('WebCMDBapi/data/machines.csv', 'w') as csv_file:
		csv_writer = csv.writer(csv_file, delimiter="|")
		csv_writer.writerow(['1 NAME', '2 ROOM', '3 IP', '4 OS', '5 OS version', '6 CATEGORY', '7 OWNER', '8 AUTHORITY', '9 BARCODE', '10 DESCRIPTION', '11 SPARE1', '12 SERIAL NUMBER', '13 HOSTID', '14 HOST STATUS', '15 INVENTORY STATUS', '16 FIREWALL', '17 TRUSTLEVEL', '18 RACKINFO', '19 POWER UP', '20 SUPPORT TEAM', '21 UUID', '22 COMMENTS'])
		for machine in machines:
			temp = [
				str(machine.hostname),
				str(machine.location),
				str(machine.ipv4),
				str(machine.os),
				str(machine.os_version),
				str(machine.physical_virtual),
				str(machine.owner),
				str(machine.administrator),
				str(machine.uofa_tag_number),
				str(machine.make_model),
				'',
				str(machine.serial_number),
				str(machine.host_id),
				str(machine.host_status),
				str(machine.status).lower(),
				str(machine.firewall),
				str(machine.trustlevel),
				str(machine.rack),
				str(machine.power_up_priority),
				str(machine.support_team),
				str(machine.id),
				str(machine.comments)
			]
			if temp[2] == 'None':
				temp[2] = ""
			csv_writer.writerow(temp)



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

