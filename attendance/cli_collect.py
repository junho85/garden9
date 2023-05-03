from attendance.garden import Garden
from datetime import date, datetime, timedelta

from attendance.service.SlackService import SlackService

garden = Garden()
slack_service = SlackService()

today = datetime.today()
start_date = today - timedelta(days=1)
end_date = today + timedelta(days=1)
# start_date = datetime.strptime('2023-02-05', "%Y-%m-%d")
# end_date = datetime.strptime('2023-02-07', "%Y-%m-%d")

oldest = start_date.timestamp()
latest = end_date.timestamp()

try:
    garden.collect_slack_messages(oldest, latest)
except Exception as err:
    slack_service.send_error_message("[모니터링] 출석부 수집 에러발생!\n" + str(err))
    raise err

