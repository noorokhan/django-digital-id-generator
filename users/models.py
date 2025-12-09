from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_file_size(value):
    limit_mb = 5
    if value.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max size is {limit_mb} MB")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    user_id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True, validators=[validate_file_size])
    photo = models.ImageField(upload_to='photos/', blank=True, null=True, validators=[validate_file_size])
    is_complete = models.BooleanField(default=False)

    def check_if_complete(self):
        return all([
            self.name.strip() != '',
            self.father_name and self.father_name.strip() != '',
            self.dob is not None,
            self.address and self.address.strip() != '',
            self.user_id_proof is not None,
            self.photo is not None
        ])

    def save(self, *args, **kwargs):
        self.is_complete = self.check_if_complete()
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_name(self):
        return f"{self.name} {self.father_name if self.father_name else ''}"
