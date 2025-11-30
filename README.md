# foodbot - cкрипт уведомлений о школьном меню в Telegram

Подходит для школ, публикующих меню в типовом формате в виде xlsx-файлов по адресу https://school-site/food/YYYY-MM-DD-sm.xlsx, где YYYY-MM-DD - текущая дата.

Скрипт скачивает меню в xlsx-формате с сайта школы, разбирает его согласно ожидаемому формату и отправляет текстовое сообщение в указанный чат Telegram.
Имеется защита от повтороного запуска в тот же день.

## Установка

* Создать virtualenv, например в каталоге env

```
virtualenv env
```
* Установить зависимости командой

```
env/bin/pip install -r requirements.txt
```
* Добавить команду запуск в crontab

## Конфигурация:

Скрипт читает конфигурационный файл `project/foodbot/foodbot-config.json`

Пример файла конфигурации:

```
{
    "source": {
        "url": "https://school-site/food/{0}-sm.xlsx",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "ignore_lines": ["итого", "всего"]
    },
    "telegram": {
        "bot_url": "https://api.telegram.org/botNNN:TOKEN",
        "chat_id": "NNNNNN",
        "message_template": "*Доброе утро!* Сегодня, {0}, в школе приготовят:\n{1}"
    }
}
```

## Запуск

```
cd project/foodbot
../../env/bin/python \_\_init\_\_.py
```


