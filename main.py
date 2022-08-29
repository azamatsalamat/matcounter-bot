import os
import telebot
import csv
from github import Github

# telegram API key
API_KEY = ''
bot = telebot.TeleBot(API_KEY)

counts_file = 'counts.csv'
words_file = 'words.csv'

dictionary = []
counts = []

ACCESS_TOKEN = ""
github = Github(ACCESS_TOKEN)
repository = github.get_user().get_repo('matcounter-bot')

file = repository.get_contents('/counts.csv').decoded_content
with open(counts_file, mode='wb') as f:
  f.write(file)

file = repository.get_contents('/words.csv').decoded_content
with open(words_file, mode='wb') as f:
  f.write(file)

with open(counts_file, mode='r', encoding='utf-8') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  for row in csv_reader:
    current_user_count = [row[0], row[1], row[2], int(row[3])]
    counts.append(current_user_count)

with open(words_file, mode='r', encoding='utf-8') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  for r in csv_reader:
    dictionary.append(r)

def write_to_file(array, filename):
  with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',')
    csv_writer.writerows(array)
   # counts_all = ""
   # for c in counts:
   #   counts_all = counts_all + str(c[0]) + ',' + str(c[1]) + ',' + str(c[2]) + ',' + str(c[3]) + "\n"
   # csv_file.write(bytes(counts_all.encode()))
  with open(filename, 'rb') as f:
    file = repository.get_contents("/" + filename)
    repository.update_file(filename, "Update data", f.read(), file.sha)

def bad_word(message):
  text = message.text.lower()
  for x in dictionary:
    if str(x[0]) in text:
      return True
  return False

def get_name(first_name, last_name):
  return ' '.join(filter(None, (first_name, last_name)))

def get_stats(chat_id):
  output = "Статистика по матам :" + "\n"
  for c in counts:
    if (c[0] == str(chat_id)):
      output = output + c[2] + ": " + str(c[3]) + "\n"
  return output

def add_word(message):
  text = message.text.lower()
  return text.startswith('/add ')

@bot.message_handler(commands=['start'])
def start(message):
  bot.send_message(message.chat.id, "Hi")

@bot.message_handler(commands=['stats'])
def stats(message):
  bot.send_message(message.chat.id, get_stats(message.chat.id))

@bot.message_handler(func=add_word)
def add(message):
  if (bot.get_chat_member(message.chat.id, message.from_user.id).status == "administrator" or bot.get_chat_member(message.chat.id, message.from_user.id).status == "creator"):
    word=message.text.split(' ')[1]
    if (len(word) > 0):
      dictionary.append([word])
      write_to_file(dictionary, words_file)
    bot.reply_to(message, 'Word ' + word + ' was added to the list')
  else:
    bot.reply_to(message, 'Only administrator can use this command')

@bot.message_handler(func=bad_word)
def reply(message):
  #bot.reply_to(message, "+1")
  for count in counts:
    if count[0] == str(message.chat.id):
      if count[1] == str(message.from_user.id):
        count[3] = count[3] + 1
        write_to_file(counts, counts_file)
        return False
  current_user = message.from_user
  current_user_count = [str(message.chat.id), str(current_user.id), get_name(current_user.first_name, current_user.last_name), 1]
  counts.append(current_user_count)
  write_to_file(counts, counts_file)
  return True

bot.polling()