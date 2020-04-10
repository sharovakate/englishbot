import requests
from bot_settings import TOKEN
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from app import Session, Users, Settings
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

bot_configuration = BotConfiguration(
    name='RinRinBot',
    avatar='http://viber.com/avatar.jpg',
    auth_token=TOKEN
)
viber = Api(bot_configuration)

CLOCK_KEYBOARD = {
"Type": "keyboard",
"Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionBody": "Начать",
            "Text": "Начать"
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            "ActionBody": "Напомнить позже",
            "Text": "Напомнить позже"
        }
    ]
}


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    session = Session()
    all_users = session.query(Users.viber_id, Users.last_time_answer)
    session.close()

    session = Session()
    settings = session.query(Settings.remind_time).filter(Settings.id_set == 1).one()
    session.close()

    for user in all_users:
        delta = datetime.utcnow() - user[1]
        print(f'delta time = {delta.seconds}')
        if delta.seconds > settings[0]:
            try:
                bot_response = TextMessage(text='Повторите слова ещё раз', keyboard=CLOCK_KEYBOARD, tracking_data='tracking_data')
                viber.send_messages(user[0], bot_response)
            except:
                print("Пользователь отписался")


@sched.scheduled_job('interval', minutes=15)
def wake_up_bot():
    r = requests.get("https://rinrinbot.herokuapp.com")
    if r.status_code == 200:
        print("bot is awake")


sched.start()
