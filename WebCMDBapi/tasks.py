from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import Computer, Server
from datetime import datetime

@shared_task(bind=True)
def import_csv_computer_task(self, data):
	progress_recorder = ProgressRecorder(self)
	result = 0
	empty = 0
	overwrite = data.pop(-1)
	total_work = len(data)
	log = ''
	for i, row in enumerate(data):
		if str(row[0]) == '': # DO NOT DEAL WITH EMPTY HOSTNAME
			empty += 1
		else:
			try:
				computer, created = Computer.objects.get_or_create(
						hostname = str(row[0]),
					)
				if overwrite:
					computer.location = str(row[1])
					computer.ipv4 = str(row[2])
					computer.ipv6 = str(row[3])
					computer.os = str(row[4])
					computer.physical_virtual = str(row[5])
					computer.owner = str(row[6])
					computer.administrator = str(row[7])
					computer.uofa_tag_number = str(row[8])
					computer.make_model = str(row[9])
					computer.cpu = str(row[10])
					computer.ram = str(row[11])
					computer.storage = str(row[12])
					computer.gpu = str(row[13])
					computer.serial_number = str(row[14])
					computer.status = str(row[15]).upper()
					computer.rack = str(row[16]),
					computer.scitech_access = str(row[17])
					computer.power_up_priority = str(row[18])
					computer.support_team = str(row[19])
					computer.department = str(row[20])
					computer.comments = str(row[21])
				computer.save()
				result += 1
			except Exception as e:
				log += f'Row:{i}; Error:{e}\n'
		progress_recorder.set_progress(i, total_work)
	f = open(f"log_celery/log{datetime.now()}.txt", "w")
	f.write(log)
	f.close()
	return f'{result}/{total_work} added; {empty} empty hostname entries; {total_work-result-empty} errors'