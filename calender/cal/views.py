from datetime import datetime, timedelta, date, time
from django.utils.safestring import mark_safe
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
import calendar
import openai
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import EventForm, AccountForm
from .models import Event, Account
from .utils import Calendar
import os
from dotenv import load_dotenv
from dateutil import parser
import json
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
    except:
        pass
    return datetime.today().date()

class CalendarView(ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('day', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['current_year'] = d.year
        context['current_month'] = d.month
        return context

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f'day={prev_month.year}-{prev_month.month}-{prev_month.day}'

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f'day={next_month.year}-{next_month.month}-{next_month.day}'

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'cal/event_form.html'

    def form_valid(self, form):
        start = form.cleaned_data['start_time'].date()
        end = form.cleaned_data['end_time'].date()
        delta = (end - start).days

        for i in range(delta + 1):
            date_for_event = start + timedelta(days=i)
            Event.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                start_time=datetime.combine(date_for_event, form.cleaned_data['start_time'].time()),
                end_time=datetime.combine(date_for_event, form.cleaned_data['end_time'].time()),
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('calendar')

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'cal/event_confirm_delete.html'
    success_url = reverse_lazy('calendar')

class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'cal/account_form.html'
    success_url = '/'

@csrf_exempt
def optimize_events(request):
    if request.method == "POST":
        now = timezone.now()
        events = list(Event.objects.filter(end_time__gte=now).values("id", "title", "start_time", "end_time"))

        if not events:
            return JsonResponse({"message": "최적화할 이벤트가 없습니다."})

        schedule_lines = [
            f"- {e['title']} ({e['start_time'].isoformat()} ~ {e['end_time'].isoformat()})"
            for e in events
        ]
        schedule_text = "\n".join(schedule_lines)

        prompt = f"""
너는 스마트한 일정 관리 도우미야. 아래는 사용자의 일정 목록이야.

- 일정들 사이의 시간이 겹치지 않도록 재배치해줘.
- 하루 시간대는 08:00 ~ 22:00만 사용 가능해.
- 일정 순서는 크게 바뀌지 않도록 유지하려 노력해줘.
- 각 일정은 최소 30분 이상이 되게 유지해.
- 제목은 그대로, 시간만 바꿔줘.

응답은 아래와 같은 형식의 JSON 배열로 줘:

[
  {{
    "title": "일정 제목",
    "start_time": "YYYY-MM-DDTHH:MM:SS",
    "end_time": "YYYY-MM-DDTHH:MM:SS"
  }},
  ...
]

✉️ 현재 일정:
{schedule_text}
"""

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "넌 일정 최적화를 도와주는 도우미야."},
                {"role": "user", "content": prompt}
            ]
        )

        output = response.choices[0].message.content
        json_text_match = re.search(r'\[.*\]', output, re.DOTALL)
        if not json_text_match:
            return JsonResponse({"error": "JSON 형식을 찾을 수 없습니다."}, status=500)

        schedule = json.loads(json_text_match.group(0))

        Event.objects.all().delete()
        for item in schedule:
            Event.objects.create(
                title=item['title'],
                start_time=parser.isoparse(item['start_time']),
                end_time=parser.isoparse(item['end_time'])
            )

        return JsonResponse({"message": "일정 최적화 완료", "output": output})

@csrf_exempt
def generate_test_events(request):
    if request.method == "POST":
        Event.objects.all().delete()
        base_date = datetime.today().replace(hour=0, minute=0)
        titles = [
            "영어 회의", "운동", "병원 예약", "점심 약속", "카페 미팅",
            "집중 공부", "팀 회의", "산책", "저녁 회식", "야근"
        ]

        for i in range(3):
            date = base_date + timedelta(days=i)
            for j, title in enumerate(titles):
                start_hour = 8 + (j * 1.5) % 12
                start_time = datetime.combine(date.date(), time(int(start_hour), int((start_hour % 1) * 60)))
                end_time = start_time + timedelta(minutes=45 + (j % 3) * 15)
                Event.objects.create(
                    title=f"{title} (Day {i+1})",
                    description="GPT 테스트용",
                    start_time=start_time,
                    end_time=end_time,
                )
        return JsonResponse({"message": "가상 일정 생성 완료"})
