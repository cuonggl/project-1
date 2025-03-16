from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
import os
from django.http import FileResponse, HttpResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('upload')
        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'upload_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def upload_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
    
    # Lấy danh sách file trong thư mục media
    uploaded_files = []
    if os.path.exists(settings.MEDIA_ROOT):
        uploaded_files = [
            {'name': f, 'url': request.build_absolute_uri(settings.MEDIA_URL + f + '/download/')}
            for f in os.listdir(settings.MEDIA_ROOT)
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, f))
        ]

    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            messages.success(request, 'File uploaded successfully!')
            # Cập nhật lại danh sách file sau khi upload
            uploaded_files = [
                {'name': f, 'url': request.build_absolute_uri(settings.MEDIA_URL + f + '/download/')}
                for f in os.listdir(settings.MEDIA_ROOT)
                if os.path.isfile(os.path.join(settings.MEDIA_ROOT, f))
            ]
        else:
            messages.error(request, 'No file selected')
    
    return render(request, 'upload_app/upload.html', {'uploaded_files': uploaded_files})

def download_file(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if os.path.exists(file_path):
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_name,
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    else:
        return HttpResponse("File not found", status=404)