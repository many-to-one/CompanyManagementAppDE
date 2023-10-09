import ast
from datetime import datetime, timedelta, date
import json
from django.core import serializers
import os
import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .utils import months_pl_shorts
from .tasks import *
from .models import (
    Documents,
    MessageCount,
    MessageCountUser,
    VacationRequest, 
    Vacations,
    Warehouse, 
    Work, 
    WorkObject, 
    WorkType, 
    Message, 
    IsRead, 
    Task,
    Subcontractor,
    )
from django.http import JsonResponse
from django.db.models import Sum, F, Prefetch
from django.contrib import messages
from users.models import CustomUser
from django.core.paginator import Paginator
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse


def index(request):
    return render(request, "home.html")

    
####################################################################################
#                                  ONLY FOR ME                                     #
####################################################################################

def getWarehouse(request):
    all_wh = Warehouse.objects.all().order_by('id')
    context = {
        'numbers': all_wh
    }

    return render(request, 'warehouse.html', context)


def newValue(request):
    if request.method == "POST":
        number = request.POST.get('number')
        value = request.POST.get('value')
        print('number ------------------ value', number, value)
        Warehouse.objects.create(
            number=number,
            value=value,
        )
    response = {
        'message': 'ok'
    }
    return JsonResponse(response)


def editValue(request):
    if request.method == "POST":
        id = request.POST.get('id')
        number = request.POST.get('number')
        print('number ------------------ value', id, number)
        wh = Warehouse.objects.get(
            id=id,
        )
        wh.number = number
        wh.save()
    response = {
        'message': 'ok'
    }
    return JsonResponse(response)


def deleteValue(request):
    if request.method == "POST":
        id = request.POST.get('id')
        wh = Warehouse.objects.get(
            id=id,
        ).delete()
        return JsonResponse({'message': 'number has been deleted!'})
    # If something wrong
    return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)


def getSearch(request):
    if request.method == "POST":
        # Get the JSON data from the request's body
        data = json.loads(request.body.decode('utf-8'))

        # Access the 'articles' list from the JSON data
        articles = data.get('articles', [])
        # Update all Warehouse objects with matching 'number' values
        Warehouse.objects.filter(number__in=articles).update(is_find=True)
        # Return the entire 'articles' list as a JSON response
        return JsonResponse({'articles': articles})
    # If something wrong
    return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)


def resetWarehouse(request):
    if request.method == "POST":
        Warehouse.objects.all().update(is_find=False)
        return JsonResponse({'message': 'Reset successful'})
    else:
        return JsonResponse({'error': 'Unsupported HTTP method'}, status=405)
    

def imageWarehouse(request):
    if request.method == 'POST' and request.FILES.get('document'):
        uploaded_file = request.FILES['document']
        # Define the path where you want to save the uploaded file
        upload_dir = 'uploads'  # Change this to your desired upload directory
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)

        # Save the uploaded file to the server
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        import easyocr
        import re

        reader = easyocr.Reader(['en'])
        result = reader.readtext(file_path, detail=0)
        #Extract the text from '[]' symbols in uploaded_file
        pattern = r'\[(.*?)\]'
        res = []
        codes = [res.append(code) for text in result for code in re.findall(pattern, text)]
        print(res)
        # Update all Warehouse objects with matching 'number' values
        Warehouse.objects.filter(number__in=res).update(is_find=True)
        response_data = {'places': res}
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)