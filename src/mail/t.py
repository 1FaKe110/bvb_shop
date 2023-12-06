import smtplib
from email.mime.text import MIMEText

# Настройки SMTP-сервера
smtp_server = 'smtp.timeweb.ru'
smtp_port = 25
smtp_username = 'ifake@test-bvb-shop.ru'
smtp_password = 'vfvfgfgf10'

# Создание объекта MIMEText для форматирования текста письма
message = MIMEText('Текст вашего сообщения')
message['Subject'] = 'Тема письма'
message['From'] = 'ifake@test-bvb-shop.ru'
message['To'] = 'gabko2016@gmail.com'

try:
    # Установка соединения с SMTP-сервером
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Отправка письма
    server.sendmail(message['From'], message['To'], message.as_string())
    server.quit()

    print('Письмо успешно отправлено!')
except Exception as e:
    print('Ошибка при отправке письма:', str(e))
