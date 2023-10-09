from django.http import JsonResponse


def header(request):
    if request.method == 'GET':
        menu_ = ''
        if 'menu' in request.GET:
            # Handle GET request with data
            menu = request.GET.get('menu')
            if menu == 'active':
                menu_ = 'active'
            else:
                menu_ = 'inactive'
            response = {
                'menu': menu_
            }
            return JsonResponse(response)
        else:
            # Handle GET request without data
            if menu_ == 'active':
                response = {
                'menu': 'active'
                }
            else:
                response = {
                'menu': 'inactive'
                }
            return JsonResponse(response)