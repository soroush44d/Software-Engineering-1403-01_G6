from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'group6'
urlpatterns = [
  path('', views.Home.as_view(), name='home'),
  path('addwords/', views.AddWords.as_view(), name='addwords'),
  path('showleitner/', views.ShowLeitner.as_view(), name='showleitner'),
  path('practice/<int:box>/', views.PracticeLeitner.as_view(), name='practicefirst'),
  path('practice/<int:box>/<int:word_id>', views.PracticeLeitner.as_view(), name='practicenext'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)