from db_structure.tables import *
from TypeTask import *
from instagrapi import Client


class InstagramBot:
    def __init__(self, db_connection):
        self.db = db_connection
        self.bot: Account = self.get_bot_instagram()
        self.check_data_account()
        self.task: Task
        self.cl: Client
        self.donor: Donor
        self.count_load_followers: int = 10

    def get_bot_instagram(self):  # need work
        bot: Account = self.db.get_bot_account()
        return bot

    def check_data_account(self):
        if self.bot.proxy is None:
            self.db.set_proxy(self.bot)
        if self.bot.user_agent is None:
            self.db.set_user_agent(self.bot)

    def get_next_task(self):
        task: Task = self.db.get_task(self.bot)
        self.task = task
        return task

    def task_processing(self):
        self.inst_login()
        if TypeTask.load_followers.value == self.task.type_id:
            self.load_followers()
        # elif TypeTask.check_bot.value == self.task.type_id:
        #     check_bot()
        # elif TypeTask.load_information.value == self.task.type_id:
        #     load_information()

        self.db.set_status_task(self.task, StatusTask.success)

    def load_followers(self):
        id_username_donor = self.get_id_username_donor()
        followers = self.request_instagram(RequestInstagram.load_followers)
        for follower in followers.values():
            user_data = UserData(username=follower.username,
                                 user_id_profile=follower.pk,
                                 pic_url_profile=follower.profile_pic_url,
                                 username_donor=self.task.username)
            self.task.follower_data.append(user_data)
            self.db.session.commit()

    def get_id_username_donor(self):
        self.donor = self.db.get_donor_id(self.task.username)
        if self.donor is None:
            id_username_donor = self.request_instagram(RequestInstagram.get_id_from_username)
            self.donor = self.db.insert_donor(self.task.username, id_username_donor)
        return self.donor.id_instagram

    def inst_login(self):
        settings = {'authorization_data': {'ds_user_id': '4100026187',
                                           'sessionid': '4100026187%3AeUmPZCd0NyJkYY%3A16',
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
                    'locale': 'ru-RU',
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

        self.cl = Client(settings)  # (self.bot.user_agent.user_agents_value)
        self.cl.login(self.bot.username, self.bot.password)

    def request_instagram(self, type_request: RequestInstagram):
        self.db.plus_count_requests(self.bot)
        if type_request == RequestInstagram.get_id_from_username:
            return self.cl.user_id_from_username(self.task.username)
        elif type_request == RequestInstagram.load_followers:
            return self.cl.user_followers(user_id=self.donor.id_instagram, amount=self.count_load_followers, use_cache=False)
