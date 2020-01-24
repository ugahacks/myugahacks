from django.core.management.base import BaseCommand, CommandError
from applications.models import Application
import os
import tarfile


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Gathering Resumes: This may take a few minutes...")
        try:
            users = Application.objects.filter(status="C") | Application.objects.filter(status="A")
            
            with tarfile.open(f"./files/resumes/resume_export.tar.gz", "w:gz") as tar_handle:
                for resume in users:
                    tar_handle.add(f"./{resume.resume.url}", resume.resume.name)
            print("Finished gathering resumes.")
        except:
            print("Error: gathering resumes.")
