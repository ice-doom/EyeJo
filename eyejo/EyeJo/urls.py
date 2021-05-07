"""EyeJo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from projectApp.views import LoginView, LogoutView
from django.conf.urls import include

urlpatterns = [
    path('api/project/', include('projectApp.urls')),
    path('api/scanTask/', include('scanTaskApp.urls')),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/logout', LogoutView.as_view(), name='logout'),
]

# urlpatterns += router.urls
# urlpatterns += [url(r'silk', include('silk.urls', namespace='silk'))]