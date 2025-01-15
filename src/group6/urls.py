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
  path('tick8/', views.Tick8View.as_view(), name='tick8view'),
  path('tickpractice/<int:user_id>/<int:stage>/', views.Tick8Practice.as_view(), name='tick8practice'),
  path('tickpractice/<int:user_id>/<int:stage>/<int:word_id>',views.Tick8Practice.as_view(), name='tick8practice'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)