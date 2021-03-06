import tarfile

from django.core.management.base import BaseCommand
from django.conf import settings

from applications.models import Application


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Gathering Resumes: This may take a few minutes...")
        try:
            users = (Application.objects.filter(status="C") | Application.objects.filter(status="A"))

            with tarfile.open(settings.EXPORT_FILES_URL + "resumes/resume_export.tar.gz", "w:gz") as tar_handle:
                for resume in users:
                    if resume.resume:
                        try:
                            tar_handle.add(f".{resume.resume.url}", resume.resume.name)
                        except Exception as f:
                            print(f"Error adding a file:{f}")
            self.stdout.write(self.style.SUCCESS("Finished gathering resumes."))
        except Exception as e:
            print(f"Error: {e}")
