from datetime import datetime
from django.shortcuts import render
from ..models import Task



def schedule(request):
    user = request.user
    if user.is_superuser:
        try:
            tasks = Task.objects.all().prefetch_related('work_object')
            done_tasks = Task.objects.filter(done=True).only('id')
            task_ids = list(done_tasks.values_list('id', flat=True))
            print('done_tasks!!!!!!!!!', task_ids)
            # done_tasks_json = serializers.serialize('json', done_tasks)
        except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd (Grafik): {e}'})
    else:
        try:
            tasks = Task.objects.filter(
                user=user
            )
            done_tasks = Task.objects.filter(done=True).only('id')
            task_ids = list(done_tasks.values_list('id', flat=True))
        except Exception as e:
            return render(request,
                          'error.html',
                          context={'error': f'Wystąpił błąd (Grafik): {e}'})

    # This code stoped work in Docker:
    # try:
    #     locale.setlocale(locale.LC_TIME, 'pl_PL')
    # except locale.Error as e:
    #     print(f"Error setting locale: {e}")
    # else:
    #     print("Locale set successfully.")

    # Abbreviated_month PL dict
    pl_month = {
        'Jan': 'Sty',
        'Feb': 'Lut',
        'Mar': 'Mar',
        'Apr': 'Kwi',
        'May': 'Maj',
        'Jun': 'Cze',
        'Jul': 'Lip',
        'Aug': 'Sie',
        'Sep': 'Wrz',
        'Oct': 'Paź',
        'Nov': 'Lis',
        'Dec': 'Gru',
    }

    if tasks:
        for task in tasks:
            date_obj = datetime.strptime(task.date, '%d %b %Y')
            formatted_date = date_obj.strftime('%d %b %Y')
            # .strip() Remove leading and trailing whitespaces from the formatted_date
            task.date_obj = date_obj
            task.abbreviated_month = pl_month[formatted_date[2:-4].strip()]
            task.save()
        context = {
            'tasks': tasks.order_by('date_obj'),
        }
        if done_tasks:
            context = {
                'tasks': tasks.order_by('date_obj'),
                'done_tasks': task_ids,
            }
    else:
        context = {
                'no_tasks': 'Na razie nie ma żadnych zadań',
            }

    return render(request, 'shedule.html', context)
