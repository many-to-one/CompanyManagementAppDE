from django.shortcuts import redirect, render, get_object_or_404
from ..tasks import *
from ..models import Documents
from django.http import JsonResponse


def upload_document(request):
    users = CustomUser.objects.values_list('username', flat=True).order_by('id')
    users_ids = CustomUser.objects.values_list('id', flat=True).order_by('id')
    documents = Documents.objects.all()
    users_ = CustomUser.objects.values('id', 'username')
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        title = request.POST['title']
        username = request.POST['user']
        user = get_object_or_404(CustomUser, username=username)
        
        document = Documents(
            title=title, 
            document=uploaded_file,
            user=user,
            )
        document.save()

        return redirect('upload_document')

    context = {
        'users': users,
        'users_ids': users_ids,
        'documents': documents,
        'users_': users_,
    }

    return render(request, 'documents.html', context)


def getDocuments(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    try:
        documents = Documents.objects.filter(user=user)
    except Exception as e:
        return render(request, 'error.html', context={'Błąd': e})
    context = {
        'documents': documents,
    }

    return render(request, 'get_documents.html', context)


def deleteDocument(request):
    if request.method == "POST":
        pk = request.POST.get('pk')
        print('pk --------------', pk)
        document = get_object_or_404(Documents, id=int(pk))
        print('document --------------', document)
        document.delete()

        response = {
            'status': 'deleted'
        }

        return JsonResponse(response)