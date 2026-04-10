import io
import json
import requests
import openpyxl
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])

from datetime import date



class MenuGetter:
    CONFIG_FILE = 'foodbot-config.json'
    LAST_PROCESSED_FILE = 'last_processed_date.txt'
    DATE_FORMAT = "%Y-%m-%d"

    config = None
    today = None
    log = None

    def run(self):
        self.log = logging.getLogger(__name__)
        self.read_config()
        self.today = date.today().strftime(self.DATE_FORMAT)
        prev_msg_id = self.check_repeat()
        if prev_msg_id:
            self.delete_message(prev_msg_id)
        xl_menu = self.fetch_menu()
        txt_menu = self.process_menu(xl_menu)
        msg_id = self.notify(txt_menu)
        self.set_result(msg_id)

    def read_config(self):
        with open(self.CONFIG_FILE, 'r') as fp:
            self.config = json.load(fp)

    def fetch_menu(self):
        r = requests.get(self.config['source']['url'].format(self.today),
            headers={'User-Agent': self.config['source']['user_agent']})
        return r.content

    def process_menu(self, xl_menu):
        output = io.StringIO()
        f = io.BytesIO(xl_menu)
        workbook = openpyxl.load_workbook(f)
        f.close()
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=4, min_col=1, max_col=4):
            if row[0].value:
                output.write("\n*" + str(row[0].value) + ":*\n")

            if row[3].value and row[3].value.lower() not in self.config['source']['ignore_lines']:
                output.write("- " + str(row[3].value).lower() + ";\n")

        rsp = output.getvalue()
        output.close()
        return rsp

    def notify(self, txt_menu):
        message = self.config['telegram']['message_template'].format(self.today, txt_menu)
        req = {
            'chat_id': self.config['telegram']['chat_id'],
            'text': message,
            'parse_mode': 'Markdown',
            'disable_notification': True
        }
        if 'message_thread_id' in self.config['telegram'] and self.config['telegram']['message_thread_id'] is not None:
            req['message_thread_id'] = self.config['telegram']['message_thread_id']

        rsp = requests.post(self.config['telegram']['bot_url'] + '/sendMessage', json=req, proxies=self.config['telegram']['proxies'])
        return rsp.json()['result']['message_id']

    def delete_message(self, msg_id):
        self.log.debug('deleting message #{0}'.format(msg_id))
        try:
            requests.post(self.config['telegram']['bot_url'] + '/deleteMessage',
            json={'chat_id': self.config['telegram']['chat_id'], 'message_id': msg_id})
        except Exception:
            self.log.exception()


    def check_repeat(self):
        prev_msg_id = None
        last_date = None
        with open(self.LAST_PROCESSED_FILE, 'a+') as fp:
            fp.seek(0)
            last_record = fp.read().strip()

            if last_record:
                if ';' in last_record:
                    last_date, prev_msg_id = last_record.split(";")
                else:
                    last_date = last_record


        if last_date and last_date == self.today:
            raise Exception('Menu already imported today')

        return prev_msg_id

    def set_result(self, msg_id):
        with open(self.LAST_PROCESSED_FILE, 'w+') as fp:
            fp.write('{0:s};{1:d}'.format(self.today, msg_id))
