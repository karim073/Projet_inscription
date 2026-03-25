import os
import requests
def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox9f025104f3fe4c29884ea9145b8bdca4.mailgun.org/messages",
  		auth=("api", os.getenv('API_KEY', 'API_KEY')),
  		data={"from": "Mailgun Sandbox <postmaster@sandbox9f025104f3fe4c29884ea9145b8bdca4.mailgun.org>",
			"to": "halima <jaddanih@gmail.com>",
  			"subject": "Hello halima",
  			"text": "Congratulations halima, you just sent an email with Mailgun! You are truly awesome!"})