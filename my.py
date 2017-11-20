import configparser

config = configparser.ConfigParser()
config.add_section('EMAIL')
config.set('EMAIL', 'mail_server', 'smtp.yandex.ru')
config.set('EMAIL', 'from_email', 'savpod@yandex.ru')
config.set('EMAIL', 'to_email', 'savsher@gmail.com')
config.set('EMAIL', 'to_email2', 'savsher@yandex.ru')
config.set('EMAIL', 'username', 'savpod')
config.set('EMAIL', 'passwd', ',tutvjnf40')
with open('webscrap.ini', 'w') as f:
    config.write(f)