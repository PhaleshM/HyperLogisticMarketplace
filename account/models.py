from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

# Custom User Manager
class UserManager(BaseUserManager):
    
    def create_user(self, email, name, tc, role, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc, and password.
        """
        
        # Check if the email is provided
        if not email:
            raise ValueError('User must have an email address')

        # Create a new user instance
        user = self.model(
            email=self.normalize_email(email),  # Normalize the email address
            name =name,
            tc   =tc,
            role =role
        )

        # Set the user's password and save the user
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None, **other_fields):
        """
        Creates and saves a superuser with the given email, name, tc, and password.
        """

        # Set the default role to "admin" if not provided
        other_fields.setdefault('role', "admin")

        # Create a superuser by calling create_user method
        user = self.create_user(
            email    = email,
            name     = name,
            tc       = tc,
            role     = other_fields['role'],
            password = password,
        )

        # Set the superuser as admin and save the user
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name = 'Email', max_length=255, unique=True)
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    # Role field for the user with choices and default value
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    # UserManager for managing user objects
    objects = UserManager()
    # Field to use as the username for authentication
    USERNAME_FIELD = 'email'
    # Additional fields required for user creation
    REQUIRED_FIELDS = ['name', 'tc', 'role']

    def __str__(self):
        # String representation of the user (email)
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always (admin has all permissions)
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always (admin has permissions for all apps)
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class AccountDetails(models.Model):
    # ForeignKey relationship with User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Field for storing UPI ID
    upi_id = models.CharField(max_length=225, null=True)
    # Field for storing credit card number
    credit_card = models.IntegerField( default=0, blank=True)
    # Field for storing debit card number
    debitt_card = models.IntegerField( default=0, blank=True)



class City(models.Model):
    # Field for storing the name of the city
    name = models.CharField(max_length=100,primary_key=True)

    def __str__(self):
        # String representation of the city (name)
        return self.name


class Region(models.Model):
    # ForeignKey relationship with City model
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='regions')
    # Field for storing the name of the region
    name = models.CharField(max_length=100)
    # Field for storing the pincode
    pincode = models.IntegerField()

    def __str__(self):
        # String representation of the region (name)
        return self.name


class Address(models.Model):
    # ForeignKey relationship with City model
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    # ForeignKey relationship with Region model
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    # Field for storing the house name/number
    house = models.CharField(max_length=100)
    # Field for storing the landmark name
    landmark = models.CharField(max_length=100,blank=True)

    def __str__(self):
        # String representation of the address (city, region)
        return f"{self.house}, {self.landmark} {self.region}, {self.city}"


