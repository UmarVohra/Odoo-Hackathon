from django.db import models
import requests
from django.db import models
from django.contrib.auth.models import User

def get_country_choices():
    url = "https://restcountries.com/v3.1/all?fields=name"
    try:
        response = requests.get(url)
        data = response.json()
        choices = [(c.get("name", {}).get("common"), c.get("name", {}).get("common")) for c in data]
        choices = sorted(list(set(choices)))
        return choices
    except:
        return []

def get_currency_choices():
    url = "https://restcountries.com/v3.1/all?fields=currencies"
    try:
        response = requests.get(url)
        data = response.json()
        choices = []
        for item in data:
            for code, details in item.get("currencies", {}).items():
                name = details.get("name")
                if name:
                    choices.append((code, name))
        choices = sorted(list(set(choices)))
        return choices
    except:
        return []

class Company(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) 
    logo = models.ImageField(blank=True,null=True)
    country = models.CharField(max_length=100, choices=get_country_choices())
    currency = models.CharField(max_length=10, choices=get_currency_choices())

    def __str__(self):
        return self.name



class User(models.Model):
    company_id = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) 
    phone = models.IntegerField(max_length=10)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_employe = models.BooleanField(default=False)
    is_finance = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)

    
    def __str__(self):
        return self.name
    
 

class Expense(models.Model):
    
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('TRAVEL', 'Travel'),
        ('HOTEL', 'Hotel'),
        ('OFFICE', 'Office Supplies'),
        ('STATIONARY', 'Stationaries'),
    ]

    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]


    employee_id = models.ForeignKey(User, on_delete=models.CASCADE)  
    description = models.TextField()
    date = models.DateField(auto_now_add=True)  
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    paid_by = models.CharField(max_length=50)  
    remarks = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    image = models.ImageField(upload_to='expenses/', blank=True, null=True)  
    percentage = models.FloatField(blank=True, null=True)  

    def __str__(self):
        return f"{self.employee.username} - {self.category} - {self.amount}"




    
