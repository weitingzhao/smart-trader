import os
from datetime import datetime
from django.db.models import QuerySet
from django.utils import timezone
from ...engine import Engine
from ..base_service import BaseService
from apps.common.models import *


class ScreeningService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.API_KEY = self.config.API_KEY_Alphavantage

    def screening_operation(self):

        # Step 0.
        # Step 0.a. prepare config and output
        file_paths = []
        folder_screenings = self.config.FOLDER_Screenings
        # Step 0.b. prepare data
        screenings = Screening.objects.all()

        # Step 1. Main function
        try:
            max_time = ScreeningOperation.objects.aggregate(max_time=models.Max('time'))['max_time']
            if max_time:
                max_time = max_time.date()

            for root, dirs, files in os.walk(folder_screenings):
                for dir_date in dirs:
                    # Skip if the dir_date is before the max_time
                    dir_date_obj = datetime.strptime(dir_date, '%Y-%m-%d').date()
                    if max_time and dir_date_obj <= max_time:
                        continue

                    dir_daily_screening = os.path.join(root, dir_date)
                    for sub_root, sub_dirs, sub_files in os.walk(dir_daily_screening):
                        for file in sub_files:
                            # Skip files that do not end with .csv
                            if not file.endswith('.csv'):
                                continue

                            file_path = os.path.join(sub_root, file)
                            file_name = os.path.basename(file_path)
                            time = datetime.strptime(dir_date, '%Y-%m-%d')
                            time = timezone.make_aware(time, timezone.get_current_timezone())

                            # Analyze file_name to determine which screening record it belongs to
                            matched_screening = None
                            for screening in screenings:
                                if file_name.startswith(screening.file_pattern):
                                    matched_screening = screening
                                    break

                            status = "1" if (matched_screening and matched_screening.status == "1") else "-1"

                            screening_operation, created = ScreeningOperation.objects.get_or_create(
                                screening=matched_screening,
                                time=time,
                                file_name=file_name,
                                defaults={'screening': matched_screening,  'status': status}
                            )

                            if not created:
                                screening_operation.time = time
                                screening_operation.file_name = file_name
                                screening_operation.status = status
                                screening_operation.save()

        except Exception as e:
            raise RuntimeError(f"An error occurred while preparing screening operations: {e}")



    def screening_snapshot(self, args: str = None)-> QuerySet[ScreeningOperation]:
        # Step 1.b. Fetch ScreeningOperation records based on args
        if args:
            id_list = [int(id_str) for id_str in args.split(',')]
            return ScreeningOperation.objects.filter(id__in=id_list)
        else:
            return ScreeningOperation.objects.filter(status=1).exclude(status="Bypass")[:20]
