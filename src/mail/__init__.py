import os
import smtplib
from email.mime.text import MIMEText

from loguru import logger


class Messages:

    @staticmethod
    def recover_password(fio, token):
        return (f'Здравствуйте, {fio} \n'
                'Мы получили запрос на восстановление пароля для вашей учетной записи. \n'
                'Чтобы восстановить доступ, пожалуйста, перейдите по ссылке ниже и '
                'следуйте инструкциям.\n'
                f'Ссылка для восстановления пароля: \n\n'
                f'\t http://80.90.184.119/set_new_password/{token}\n\n'
                f'Если вы не запрашивали восстановление пароля, пожалуйста, проигнорируйте это сообщение.\n\n'
                f'С уважением,\n'
                f'Команда поддержки')

    @staticmethod
    def order_notice(fio, order, positions):
        header = (f'Здравствуйте, {fio}! \n\n'
                f'Мы получили заказ №{order.id} от {order.creation_time[:10]}\n'
                'Позиции в заказе:\n')
        positions = '\n'.join([f'- {position.id} | {position.name} | {position.price} x {positions.amount} шт.'
                     for position in positions])
        total = (f'Сумма заказа: {order.total_price}'
                'следуйте инструкциям.\n'
                f'Ссылка для восстановления пароля: \n\n'
                f'\t http://80.90.184.119/set_new_password/{token}\n\n'
                f'Если вы не запрашивали восстановление пароля, пожалуйста, проигнорируйте это сообщение.\n\n'
                f'С уважением,\n'
                f'Команда поддержки')


class Mailer:

    def __init__(self):
        self.host = os.getenv('smpt_host')
        self.port = int(os.getenv('smpt_port'))
        self.login = os.getenv('smpt_login')
        self.password = os.getenv('smpt_password')

    def recover_password(self, email, fio, token):
        message = MIMEText(Messages.recover_password(fio, token))
        message['Subject'] = 'Восстановление пароля'
        message['From'] = 'ifake@test-bvb-shop.ru'
        message['To'] = email

        try:
            # Установка соединения с SMTP-сервером
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.login, self.password)

            # Отправка письма
            server.sendmail(message['From'], message['To'], message.as_string())
            server.quit()

            logger.info(f"Сообщение для восстановления пароля отправлено на {email}")
        except Exception as e:
            logger.error(f'Ошибка при отправке письма: {e}')


def test_mail():
    mailer = Mailer()
    mailer.recover_password('gabko2016@gmail.com',
                            'Габко Николай',
                            123)


if __name__ == '__main__':
    test_mail()
