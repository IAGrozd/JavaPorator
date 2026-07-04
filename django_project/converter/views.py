import io
from django.contrib import messages
import zipfile
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .rules import apply_rules
from django.contrib.auth.forms import UserCreationForm
from .scanner import JavaScanner
from .scan_exceptions import *

@login_required
def converter_home(request):
    if request.method == 'POST' and request.FILES.getlist('java_files'):
        java_files = request.FILES.getlist('java_files')
        
        zip_buffer = io.BytesIO()
        scanner = JavaScanner()
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file in java_files:
                    java_code = file.read().decode('utf-8')
                    
                    python_code = scanner.transform(apply_rules(java_code))
                    
                    new_filename = file.name.replace('.java', '.py')
                    if not new_filename.endswith('.py'):
                        new_filename += '.py'
                    
                    zip_file.writestr(new_filename, python_code)
            
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="translated_python_files.zip"'
            
            return response
        except JavaSyntaxError as e:
            messages.error(request, str(e))
            return render(request, 'index.html')
        except ConversionError as e:
            messages.error(request, str(e))
            return render(request, 'index.html')
        except Exception as e:
            messages.error(request, f"Unknown error occured!")
            return render(request, 'index.html')


    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})