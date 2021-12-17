import inspect
import random
import time
import traceback

from instagrapi.exceptions import ClientNotFoundError

from db_structure.tables import *
from types_enum import *
from instagrapi import Client


class InstagramBot:
    def __init__(self, db_connection):
        self.db = db_connection
        self.bot: Account
        self.task: Task
        self.cl: Client
        self.donor: Donor
        self.count_load_followers: int = 10
        self.start_sec = 10
        self.end_sec = 15
        self.count_requests = 200

    def get_bot_instagram(self):  # need work
        self.bot: Account = self.db.get_bot_account()
        if self.bot is None:
            print(f'Бот для обработки - отсутствует')
            return False
        self.check_data_account()
        print('Бот для обработки - id:', self.bot.id)
        print(f'Count_requests - {self.bot.count_requests}')
        return True

    def check_data_account(self):
        if self.bot.proxy is None:
            self.db.set_proxy(self.bot)
        if self.bot.user_agent is None:
            self.db.set_user_agent(self.bot)
        self.bot.log_error = None

    def get_next_task(self, id: int = None):
        task: Task = self.db.get_task(self.bot, id)
        self.task = task
        if task is not None:
            print(f'Задача получена - id: {self.task.id}')
            return True
        else:
            print(f'Задачи отсутствуют')
            return False

    def task_processing(self):
        if TypesTask.load_followers.value == self.task.type_id:
            print('load_followers -', self.task.username)
            self.load_followers()
        elif TypesTask.load_information.value == self.task.type_id:
            print('load_information -', self.task.username)
            self.load_information()
        self.db.set_status_task(self.bot, self.task, StatusTask.success)

    def load_followers(self):
        id_username_donor = self.get_id_username_donor()
        followers = self.request_instagram(RequestInstagram.load_followers)
        if len(followers) > 0:
            for follower in followers.values():
                user_data = UserData(username=follower.username,
                                     user_id_profile=follower.pk,
                                     pic_url_profile=follower.profile_pic_url,
                                     username_donor=self.task.username)
                new_task = self.db.create_task_load_followers(follower.username, self.task.id_username_parent)
                self.db.add_follower(user_data, new_task)
                print('follower was registered - ', follower.username)

    def load_information(self):
        print('Выгружаю информацию о пользователе')
        follower_info = self.request_instagram(RequestInstagram.load_info_follower)
        if follower_info.media_count > 2 and follower_info.is_private == False:
            print('Выгружаю медиа пользователя')
            follower_media_id: str = self.request_instagram(RequestInstagram.get_media_id)
        else:
            follower_media_id = ''
        self.db.update_follower_info(follower_info, follower_media_id, self.task)
        is_bot = self.check_is_bot()
        self.db.set_bot_status(is_bot, self.task.follower_data[0])
        print('info was registered - ', follower_info.username)

    def get_id_username_donor(self):
        self.donor = self.db.get_donor_id(self.task.username)
        if self.donor is None:
            id_username_donor = self.request_instagram(RequestInstagram.get_id_from_username)
            self.donor = self.db.insert_donor(self.task.username, id_username_donor)
        return self.donor.id_instagram

    def inst_login(self):
        settings = {'authorization_data': {'ds_user_id': '4100026187',
                                           'should_use_header_over_cookies': True},
                    'cookies': {},
                    'country': 'RUS',
                    'device_settings': {'android_release': '8.0.0',
                                        'android_version': 26,
                                        'app_version': '194.0.0.36.172',
                                        'cpu': 'qcom',
                                        'device': 'MI 5s',
                                        'dpi': '480dpi',
                                        'manufacturer': 'Xiaomi',
                                        'model': 'capricorn',
                                        'resolution': '1080x1920',
                                        'version_code': '301484483'},
                    'last_login': 1628691119.1710863,
                    'locale': 'en-EN',
                    'timezone_offset': 10800,
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 ('
                                  'KHTML, like Gecko) Mobile/15E148 Instagram 123.0.0.24.115 (iPhone11,8; iOS 13_3; '
                                  'en_US; en-US; scale=2.00; 828x1792; 188362626)',
                    'uuids': {'advertising_id': '1e71a894-5b2b-49d5-b32d-70ce8000f1cf',
                              'android_device_id': 'android-4c96d0f34ff79043',
                              'client_session_id': '22ce0e00-0574-434e-b6c2-5a8f979e2065',
                              'phone_id': 'edd18389-4c18-4227-884d-c03db9a91749',
                              'request_id': 'd0b79970-a7cd-4063-85c3-4c02e9387138',
                              'tray_session_id': '62641269-d973-40f1-ad35-845668cb2cbb',
                              'uuid': '4f43dbb2-cfea-47c5-86a0-7e689bf3143c'}}
        try:
            self.cl = Client()  # (self.bot.user_agent.user_agents_value)
            self.cl.load_settings('dump.json')
            # self.cl.set_proxy('http://bwgtywas:nuv3htbw4lmd@209.127.191.180:9279')
            # self.cl.set_user_agent('Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.0.0.24.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00; 828x1792; 188362626)')
            self.cl.login(self.bot.username, self.bot.password)
            #self.cl.dump_settings('dump.json')
            self.cl.request_timeout = 30
            print('Авторизация в instagram прошла успешно')
        except Exception as ex:
            print('Ошибка авторизации в instagram: ', ex)

    def request_instagram(self, type_request: RequestInstagram):
        self.db.plus_count_requests(self.bot)
        if type_request == RequestInstagram.get_id_from_username:
            result = self.cl.user_id_from_username(self.task.username)
        elif type_request == RequestInstagram.load_followers:
            result = self.cl.user_followers(user_id=self.donor.id_instagram, amount=self.count_load_followers)
        elif type_request == RequestInstagram.load_info_follower:
            result = self.cl.user_info(self.task.follower_data[0].user_id_profile)
        elif type_request == RequestInstagram.get_media_id:
            try:
                result = self.cl.user_medias(self.task.follower_data[0].user_id_profile, 3)[-1].id
            except IndexError:
                result = self.cl.user_medias(self.task.follower_data[0].user_id_profile, 3)

        time.sleep(random.randint(self.start_sec, self.end_sec))
        return result

    def check_is_bot(self):
        print('Проверка на бота')
        follower: UserData = self.task.follower_data[0]
        image_missing = '44884218_345707102882519_2446069589734326272' in follower.pic_url_profile
        count_media = follower.media_count_profile < 3
        if follower.follower_count_profile == 0: return 1
        following_procent = follower.following_count_profile / follower.follower_count_profile >= 2
        if image_missing or count_media or following_procent:
            return 1
        else:
            return 0

    def tasks_working(self):
        self.inst_login()
        while self.bot.count_requests < self.count_requests:
            if self.get_next_task():
                try:
                    self.task_processing()
                except ClientNotFoundError:
                    pass
                except Exception as e:
                    traceback.print_exc()
                    info = inspect.trace()[-1]
                    print(f"Возникла ошибка по задаче: {info}")
                    self.db.log_error(self.task, self.bot, e, info)
                    self.db.set_status_task(task=self.task, account=self.bot, status=StatusTask.error, message=e)
                    continue
            else:
                break
            print('-' * 10)