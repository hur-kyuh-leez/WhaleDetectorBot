import requests

string = 'TESTING'
telegram_url = 'https://api.telegram.org/bot603284903:AAGqMlAWEHgZkQB1acqqMjTLjSiSdgLQu5U/sendMessage?chat_id=-1001282967157&text=%s' % string
r = requests.post(telegram_url)
print(r.text)
print(r.status_code)

print(telegram_url)
