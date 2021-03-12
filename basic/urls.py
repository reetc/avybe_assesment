from django.conf.urls import url
from basic import views

app_name = 'basic'

urlpatterns=[
    url(r'^update/$',views.update,name='update'),
    url(r'^register/$',views.register,name='register'),
    url(r'^user_login/$',views.user_login,name='user_login'),
]
