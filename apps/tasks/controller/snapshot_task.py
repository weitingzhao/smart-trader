from .base_task import BaseTask
import os
from typing import List
from django.conf import settings
from tablib import Dataset
from logics.logic import Logic
from apps.common.models import *
from django.core.files.base import ContentFile
from django.utils import timezone
from django_celery_results.models import TaskResult
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more

class SnapshotTask(BaseTask):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [
            {"name":"dry run (oldest 20 or customize)"},
            {"name":"Import (oldest 20 or customize)"}
        ]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'dry run (oldest 20 or customize)':
            self.fetching_snapshot(dry_run=True, args=args)
        elif script_name == 'Import (oldest 20 or customize)':
            self.fetching_snapshot(dry_run=False, args=args)


    def fetching_snapshot(self,  dry_run, args: str = None):

        # Step 1.  Get the screening operations
        operations = instance.service.fetching().screening().screening_snapshot(args)

        # Initialize the count
        total_operations = 0
        total_resources = 0

        # Step 2. Loop through the screening operations
        for operation_job in operations:
            # Step 2.a prepare screening operation_job task
            file_name = operation_job.file_name
            folder = instance.config.FOLDER_Screenings
            date_part = operation_job.time.strftime('%Y-%m-%d')
            file_path = os.path.join(folder, date_part, file_name)

            # Step 2.b Get the screening record based on screening_id
            screening = Screening.objects.get(screening_id=operation_job.screening_id)
            # Step 2.c Retrieve the matched value from settings.IMPORT_EXPORT_CELERY_MODEL_DEPENDENCY
            models = settings.IMPORT_EXPORT_CELERY_MODEL_DEPENDENCY.get(screening.import_models)
            if not models:
                continue
            # Step 2.d Read the file to dataset
            with open(file_path, 'r') as file:
                dataset = Dataset().load(file.read(), format='csv')

            # Step 4. Loop through models and create Import Job & Dry Run
            processed_result = ''
            errors = ''
            for model in models:
                resource_class = model()
                resource = resource_class()
                # Step 4.b use the resource to import data
                result = resource.import_data(dataset, dry_run=dry_run, file_name=file_name)
                errors += str(result.row_errors()) if result.has_errors() else ''
                # self._run_import_job(operation_job, resource, result, dry_run=dry_run)

                model_processed_result = (
                    f"Import Model: {model.__name__}:"
                    f"New: {result.totals['new']}, "
                    f"Updated: {result.totals['update']}, "
                    f"Skipped: {result.totals['skip']}, "
                    f"Error: {result.totals['error']},"
                    f"file_path: {file_path}")

                processed_result += model_processed_result + "\n"
                total_resources += 1

            # Step 5. Update the screening operation_job record.
            operation_job.processed_at = timezone.now()
            operation_job.status =  ScreeningOperationChoices.FAILED if len(errors) > 1 else ScreeningOperationChoices.DONE
            operation_job.processed_result = processed_result
            operation_job.errors = errors
            operation_job.save()
            print(processed_result)

            # Increment the count
            total_operations += 1


        # Return JSON response
        json = {"output": f"successful process {total_operations} file & {total_resources} resources"}
        self.celery.update_state(state='SUCCESS', meta=json)
        return json

    @staticmethod
    def _run_import_job(operation_job, resource, result, dry_run=True):

        skip_diff = resource._meta.skip_diff or resource._meta.skip_html_diff

        for error in result.base_errors:
            operation_job.errors += f"\n{error.error}\n{error.traceback}\n"
        for line, errors in result.row_errors():
            for error in errors:
                operation_job.errors += _("Line: %s - %s\n\t%s\n%s") % (
                    line,
                    error.error,
                    ",".join(str(s) for s in error.row.values()),
                    error.traceback,
                )

        if dry_run:
            summary = "<html>"
            summary += "<head>"
            summary += '<meta charset="utf-8">'
            summary += "</head>"
            summary += "<body>"
            summary += (  # TODO refactor the existing template so we can use it for this
                '<table  border="1">'
            )
            # https://github.com/django-import-export/django-import-export/blob/6575c3e1d89725701e918696fbc531aeb192a6f7/import_export/templates/admin/import_export/import.html
            if not result.invalid_rows and not skip_diff:
                cols = lambda row: "</td><td>".join([field for field in row.diff])
                summary += (
                    "<tr><td>change_type</td><td>"
                    + "</td><td>".join(
                        [f.column_name for f in resource.get_user_visible_fields()]
                    )
                    + "</td></tr>"
                )
                summary += (
                    "<tr><td>"
                    + "</td></tr><tr><td>".join(
                        [
                            row.import_type + "</td><td>" + cols(row)
                            for row in result.valid_rows()
                        ]
                    )
                    + "</tr>"
                )
            else:
                cols = lambda row: "</td><td>".join(
                    [str(field) for field in row.values]
                )
                cols_error = lambda row: "".join(
                    [
                        "<mark>"
                        + key
                        + "</mark>"
                        + "<br>"
                        + row.error.message_dict[key][0]
                        + "<br>"
                        for key in row.error.message_dict.keys()
                    ]
                )
                summary += (
                    "<tr><td>row</td>"
                    + "<td>errors</td><td>"
                    + "</td><td>".join(
                        [f.column_name for f in resource.get_user_visible_fields()]
                    )
                    + "</td></tr>"
                )
                summary += (
                    "<tr><td>"
                    + "</td><td></td></tr><tr><td>".join(
                        [
                            str(row.number)
                            + "</td><td>"
                            + cols_error(row)
                            + "</td><td>"
                            + cols(row)
                            for row in result.invalid_rows
                        ]
                    )
                    + "</tr>"
                )
            summary += "</table>"
            summary += "</body>"
            summary += "</html>"
            operation_job.change_summary.save(
                os.path.split(operation_job.file_name)[1] + ".html",
                ContentFile(summary.encode("utf-8")),
            )
        else:
            operation_job.imported = timezone.now()
            operation_job.processed_result = f"Import job finished dry_run: {dry_run}"
        operation_job.save()


# # Step 3. Save file to media folder and create import job
# # Step 3.a Initialize the storage class
# storage_class = lazy_initialize_storage_class()
# # Step 3.b Read the file content
# with open(file_path, 'rb') as file:
#     file_content = file.read()
# # Step 3.c Define the destination path in the media folder
# file_name = os.path.basename(file_path)
# # Step 3.d. Define the destination path in the media folder
# destination_path = os.path.join('django-import-export-celery-import-jobs', file_name)
# # Step 3.e. Save the file to the media folder using the storage class
# storage_class.save(destination_path, ContentFile(file_content))
# # Step 4.c Create an import job (no need this import job since above script can do the import work already
# import_job = ImportJob.objects.create(
#     file=destination_path,
#     format='text/csv',
#     model=screening.celery_models,
#     job_status='pending',
#     errors=errors
# )
# def lazy_initialize_storage_class():
#     from django.conf import settings
#     try:
#         from django.core.files.storage import storages
#         storages_defined = True
#     except ImportError:
#         storages_defined = False
#
#     if not hasattr(settings, 'IMPORT_EXPORT_CELERY_STORAGE') and storages_defined:
#         # Use new style storages if defined
#         storage_alias = getattr(settings, "IMPORT_EXPORT_CELERY_STORAGE_ALIAS", "default")
#         storage_class = storages[storage_alias]
#     else:
#         # Use old style storages if defined
#         from django.core.files.storage import get_storage_class
#         storage_class = get_storage_class(getattr(settings, "IMPORT_EXPORT_CELERY_STORAGE", "django.core.files.storage.FileSystemStorage"))
#         return storage_class()
#
#     return storage_class


# Create your views here.
instance = Logic()
