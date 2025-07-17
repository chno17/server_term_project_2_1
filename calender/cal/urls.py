from django.urls import path
from .views import CalendarView, EventCreateView, EventDeleteView, AccountCreateView, optimize_events, generate_test_events 

app_name = 'cal'

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'), #main 페이지를 가져옴
    path('event/new/', EventCreateView.as_view(), name='event_new'), #일정 생성 페이지를 가져옴
    path('event/delete/<int:pk>/', EventDeleteView.as_view(), name='event_delete'), #일정 삭제 페이지 가져옴
    path('account/new/', AccountCreateView.as_view(), name='account'), #가계부 추가 페이지 가져옴
    path('optimize-events/', optimize_events, name='optimize_events'),
    path('generate-test-events/', generate_test_events, name='generate_test_events'),
]

