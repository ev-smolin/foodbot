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
        self.today = date.today().strftime(self.DATE_FORMAT)
        self.check_repeat()
        self.read_config()
        xl_menu = self.fetch_menu()
        txt_menu = self.process_menu(xl_menu)
        self.notify(txt_menu)
        self.set_date()

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

            if row[3].value:
                output.write("- " + str(row[3].value).lower() + ";\n")

        rsp = output.getvalue()
        output.close()
        return rsp

    def notify(self, txt_menu):
        message = self.config['telegram']['message_template'].format(self.today, txt_menu)
        requests.post(self.config['telegram']['bot_url'] + '/sendMessage',
            json={'chat_id': self.config['telegram']['chat_id'], 'text': message, 'parse_mode': 'Markdown'})


    def check_repeat(self):
        with open(self.LAST_PROCESSED_FILE, 'a+') as fp:
            fp.seek(0)
            last = fp.read().strip()

        if last and last == self.today:
            raise Exception('Menu already imported today')

    def set_date(self):
        with open(self.LAST_PROCESSED_FILE, 'w+') as fp:
            fp.write(self.today)
