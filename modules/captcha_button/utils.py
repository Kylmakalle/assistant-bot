from random import randint

from aiogram.utils.markdown import quote_html


def random_equation():
    num_a = randint(-15, 15)
    num_b = randint(-10, 10)
    answer = num_a + num_b
    fake_answer = randint(-25, 25)
    while fake_answer == answer:
        fake_answer = randint(-25, 25)
    return {'a': num_a, 'b': num_b, 'answer': answer, 'fake_answer': fake_answer}


def get_welcome_message(chat, user, chat_db=None):
    if chat_db and chat_db.get('welcome_message'):
        return {'message': chat_db['welcome_message'].format(USER_ID=user['id'], FIRST_NAME=user['first_name'],
                                                             TITLE=chat['title'],
                                                             VAR_A=chat_db['welcome_var_a'],
                                                             VAR_B=chat_db['welcome_var_b']),
                'VAR_A': chat_db['welcome_var_a'],
                'VAR_B': chat_db['welcome_var_b'], 'type': 'themed'}
    else:
        equation = random_equation()
        sample_welcome_message = 'Привет, <a href="tg://user?id={}">{}</a>! Добро пожаловать в <b>{}</b>.\n' \
                                 'Сколько будет {} + {}?'.format(user['id'], user['first_name'], quote_html(chat.title),
                                                                 equation['a'], equation['b'],
                                                                 VAR_A=equation['answer'],
                                                                 VAR_B=equation['fake_answer'])
        return {'message': sample_welcome_message, 'VAR_A': equation['answer'], 'VAR_B': equation['fake_answer'],
                'type': 'sample'}
