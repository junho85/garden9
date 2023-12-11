import logging
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .garden import Garden
import pprint
import markdown
from python_markdown_slack import PythonMarkdownSlack

from .service.AttendanceService import AttendanceService


def index(request):
    garden = Garden()
    context = {
        "start_date": garden.get_start_date_str(),
        "gardening_days": garden.get_gardening_days()
    }
    return render(request, 'attendance/index.html', context)


# 정원사들 리스트
def users(request):
    garden = Garden()
    users = garden.get_users()
    return JsonResponse(users, safe=False)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# 유저별 출석부
def user(request, user):
    garden = Garden()
    context = {
        "user": user,
        "start_date": garden.get_start_date_str(),
        "gardening_days": garden.get_gardening_days()
    }

    return render(request, 'attendance/users.html', context)


# 유저의 출석데이터
def user_api(request, user):
    attendance_service = AttendanceService()
    attendances = attendance_service.find_attendances_by_user(user)

    output = []
    for (date, commits) in attendances.items():
        for commit in commits:
            commit["message"] = markdown.markdown(commit["message"], extensions=[PythonMarkdownSlack()])
            # commit["message"] = "<br>".join(commit["message"].split("\n"))
        output.append({"date": date, "commits": commits})

    # logging.info(output)
    return JsonResponse(output, safe=False)


def collect(request):
    """
    slack_messages 수집
    :param request:
    :return:
    """
    # yyyy-mm-dd
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    if start_str is None:
        today = datetime.today()
        start_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")  # yesterday

    if end_str is None:
        today = datetime.today()
        end_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")  # tomorrow

    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")

    oldest = start.timestamp()
    latest = end.timestamp()

    garden = Garden()
    result = garden.collect_slack_messages(oldest, latest)

    return JsonResponse(result, safe=False)


def manual_insert(request):
    """
    수동 출석부 입력
    :param request:
    :return:
    """
    commit_url = request.GET.get('commit_url')
    garden = Garden()
    result = garden.manual_insert(commit_url)

    return JsonResponse(result, safe=False)


def get(request, date_str):
    """
    특정일의 출석 데이터 불러오기
    :param request:
    :param date_str: str, yyyymmdd
    :return:
    """
    garden = Garden()
    attendance_service = AttendanceService()
    result = attendance_service.get_attendances(users=garden.get_users(),
                                                date=datetime.strptime(date_str, "%Y%m%d").date())
    return JsonResponse(result, safe=False)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def gets(request):
    """
    전체 출석부 조회
    :param request:
    :return:
    """
    garden = Garden()
    attendance_service = AttendanceService()

    result = []

    users = garden.get_users()
    for user in users:
        attendances = attendance_service.find_attendances_by_user(user)

        # convert key type datetime.date to string
        for key_date in list(attendances.keys()).copy():
            formatted_date = key_date.strftime("%Y-%m-%d")
            attendances[formatted_date] = attendances.pop(key_date)[0]["ts"]

        result.append({"user": user, "attendances": attendances})

    return JsonResponse(result, safe=False)
