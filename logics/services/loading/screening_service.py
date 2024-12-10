from django.db.models import Q
from django.utils import timezone
from apps.common.models import *
from logics.engine import Engine
from logics.services.base_service import BaseService
from import_export_celery import tasks
from whoosh.qparser import MultifieldParser, WildcardPlugin, OrGroup
from home.singleton import Instance

class ScreeningService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    def snapshot_job(self):

        # Step 1. Get ScreeningOperation records with import_job_id and status DRY_RUNED
        screening_operations = ScreeningOperation.objects.filter(
            import_job_id__isnull=False,
            status=ScreeningOperationChoices.DRY_RUNED
        )

        # Step 2. Process the screening operations
        for operation in screening_operations:
            try:
                # Get the ImportJob record based on import_job_id
                import_job = ImportJob.objects.get(id=operation.import_job_id)
                # Log the import job information
                tasks.logger.info("Importing %s dry-run: False" % (import_job.pk))
                # Run the import job with dry_run=False
                tasks.run_import_job.delay(import_job.pk, dry_run=False)

                # Step 3. Update the screening operation record.
                processed_result = f"Real: operation id: {operation.id} job id:{import_job.id}"
                operation.processed_at = timezone.now()
                operation.status = ScreeningOperationChoices.DONE
                operation.processed_result = processed_result
                operation.save()
            except Exception as e:
                # If an error occurs, update the operation status to FAILED
                operation.status = ScreeningOperationChoices.FAILED
                operation.errors = str(e)
                operation.save()
                tasks.logger.error(f"Failed to import job {import_job.pk}: {e}")

        return screening_operations