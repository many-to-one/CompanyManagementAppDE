from django.shortcuts import render

from django.http import HttpResponse

from users.models import CustomUser
def index(request):
    return render(request, "home.html")


def userWork(request, pk):
    if request.method == 'POST':
        date = request.POST.get('date')
        timestart = request.POST.get('timestart')
        timefinish = request.POST.get('timefinish')
        print(date, timestart, timefinish)
    user = CustomUser.objects.get(id=pk)
    context = {'user': user}
    return render(request, 'user_work.html', context)
