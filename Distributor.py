from db_structure.tables import *

class Distributor():
    def __init__(self, db_connection):
        self.db = db_connection

    def registration_tasks(self):
        accounts = self.db.get_accounts_for_registration()
        for row in accounts.all():
            acc: Account = row
            source_accounts = acc.account_settings.source_accounts.split(';')
            self.db.create_tasks(acc, source_accounts)
