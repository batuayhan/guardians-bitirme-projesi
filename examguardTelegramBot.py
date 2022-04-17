import requests
import json



def sendMessage(bot_message):
    f = open('telegramBotCredentials.json')
    data = json.load(f)


    bot_token = data["token"]
    bot_chatID = data["chat_id"]
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()
