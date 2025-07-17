from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Event, Account
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy, reverse

# HTML 기반의 달력을 생성하는 커스텀 Calendar 클래스
class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # 하루에 대한 HTML을 생성 (이벤트 리스트와 가계부 합산 포함)
    def formatday(self, day, events, accounts):
        if day == 0:
            return "<td></td>"

        # 해당 일자의 총 수입/지출 합계 계산
        total = sum(a.amount for a in accounts.filter(date__day=day))
        # 해당 일자의 이벤트 리스트 생성
        events_per_day = events.filter(start_time__day=day)
        d = ''.join(
            f'<li>{e.title} <a href="{reverse("cal:event_delete", args=[e.id])}"><삭제></a></li>'
            for e in events_per_day
)

        return f"<td><span class='date'>{day}</span><ul>{d}</ul><div>{total}원</div></td>"

    # 주 단위로 한 주의 HTML 생성
    def formatweek(self, theweek, events, accounts):
        return f"<tr>{''.join(self.formatday(d, events, accounts) for d, _ in theweek)}</tr>"

    # 월 단위 달력 전체 HTML 생성
    def formatmonth(self, withyear=True):
        events = Event.objects.filter(
            start_time__year=self.year,
            start_time__month=self.month
        )
        accounts = Account.objects.filter(
            date__year=self.year,
            date__month=self.month
        )

        cal = '<table class="table table-bordered">\n'
        cal += f'<tr>{"".join(f"<th>{day}</th>" for day in ["월", "화", "수", "목", "금", "토", "일"])}</tr>\n'

        for week in self.monthdays2calendar(self.year, self.month):
            cal += self.formatweek(week, events, accounts)

        cal += '</table>'
        return cal


# 이벤트 삭제 처리용 클래스 뷰
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'cal/event_confirm_delete.html'
    success_url = reverse_lazy('calendar')  # 삭제 완료 후 달력 페이지로 리디렉션
