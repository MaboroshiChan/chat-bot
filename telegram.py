import telebot
import openai
import os
import copy

API_KEY = "6268910115:AAEJKC83WqHKSoz4nN0Ckn3XXb0Z9ompGaY"
openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_CHAT_HIST = 10

bot = telebot.TeleBot(API_KEY)

with open("prompt.txt", "r") as f:
    prompt = f.read()

chat_cache = [{
        "role": "girl", "content": 
            prompt
    }]

completion_cache = [prompt]

def print_chat_cache(chat_cache):
    print("chat history: ")
    for c in chat_cache:
        print(c)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print("received message from start command: ", message.text)
    bot.send_message(message.chat.id, "*Welcome to the Mabotroshi*" + message.text, parse_mode="Markdown")

@bot.message_handler(commands=['delete'])
def delete_message(message):
    print("delete message")
    bot.delete_message(message.chat.id, message.message_id - 2)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "*Help*", parse_mode="Markdown")

@bot.message_handler(commands=['me'])
def send_as_me(message):
    bot.delete_message(message.chat.id, message.message_id)
    get_body = message.text.split(" ", 1)
    if len(get_body) == 1:
        return
    else:
        # send message as me
        chat_cache.append({"role": "me", "content": get_body[1]})
        print("chat history: ", chat_cache)
        bot.send_message(message.chat.id, get_body[1])

@bot.message_handler(commands=['girl'])
def send_as_girl_but_do_not_evaluate_instantly(message):
    get_body = message.text.split(" ", 1)
    if len(get_body) == 1:
        return
    else:
        # send message as girl
        # but do not evaluate instantly
        chat_cache.append({"role":"girl", "content": get_body[1]})
        print_chat_cache(chat_cache)

@bot.message_handler(content_types=['text'])
def chat_davinci(message):
    try:
        #completion_cache.append("女生：" + message.text + "\n\n")
        chat_cache.append({
            "role": "girl",
            "content": message.text + "\n\n"
        })
        for k in chat_cache:
            completion_cache.append(k['role'] + ": " + k['content'] + "\n\n")
        print("completion cache: ", completion_cache)

        to_send=""
        for t in completion_cache:
            to_send+=t
        bot.send_message(message.chat.id, "Please wait while I think...")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=to_send,
            temperature=0.5,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        bot.delete_message(message.chat.id, message.message_id + 1)
        resp = response.choices[0].text.split(":", 1)[1]
        bot.send_message(message.chat.id, resp)
        #completion_cache.append(response.choices[0].text + "\n\n")
        chat_cache.append({
            "role": "me",
            "content": resp
        })
    except Exception as e:
        print("error: ", e)
        bot.send_message(message.chat.id, "We had an error, please try again later")

    print("received message", message.text)

@bot.message_handler(content_types=['/text'])
def chat_mode(message):
    print("received message: ", message.text)
    chat_cache.append({"role": "girl", "content": message.text})
    print_chat_cache(chat_cache)
    try:
        bot.send_message(message.chat.id, "Please wait while I think...")
        messages = copy.deepcopy(chat_cache)

        # change name of roles
        for mes in messages: 
            if mes["role"] == "girl":
                mes["role"] = "user"
            elif mes["role"] == "me":
                mes["role"] = "assistant"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        if response.choices:
            content = response.choices[0].message.content
            print("response: ", content)
            if len(chat_cache) == MAX_CHAT_HIST:
                del chat_cache[1]
            chat_cache.append({"role": "me", "content": content})
            bot.delete_message(message.chat.id, message.message_id + 1)
            bot.send_message(message.chat.id, content)
    except Exception as e:
        print("error: ", e)
        bot.send_message(message.chat.id, "We had an error, please try again later")

@bot.message_handler(content_types=['/continue'])
def continue_chat(message):
    ## TODO: Complete this function
    # 1. Get the last messages from the chat cache
    # 2. Send the last messages to the openai api
    # 3. Send the response to the user
    # 4. Add the response to the chat cache
    pass

print("Bot is running...")
bot.polling()