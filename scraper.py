from flask import Flask, request, redirect
import twilio.twiml
from bs4 import BeautifulSoup
import re
import string
import urllib

app = Flask(__name__)

def get_rhyme_list(word):
	# get the html
	url = "http://www.rhymezone.com/r/rhyme.cgi?Word=" + word + "&typeofrhyme=perfect&org1=syl&org2=l&org3=y"
	site = urllib.urlopen(url)
	# import page
	soup = BeautifulSoup(site)
	# get list of a and b tags containing rhymes
	rhyme_list_unparsed = soup.find(text=re.compile("Words and phrases that rhyme with")).parent.find_next_siblings(re.compile('^a$|^b$'))
	# create a list of rhymes (parsed tags)
	rhyme_list = []
	for tag in rhyme_list_unparsed:
		if tag.name == 'a':
			rhyme_list.append(string.replace(unicode(tag.string), u'\xa0', u' '))
		# otherwise tag.name == 'b'
		elif len(tag.contents) == 1 and len(tag('a',recursive=False)) == 1:
			rhyme_list.append(string.replace(unicode(tag.contents[0].string), u'\xa0', u' '))
	return rhyme_list

@app.route("/", methods=['GET', 'POST'])
def hello():
	"""Respond to an incoming sms consisting of one word with a list of words and phrases that rhyme with that word."""

	word = request.values.get('Body')
	rhyme_list = get_rhyme_list(word)
	text = ""
	while len(rhyme_list) > 0 and len(text) + len rhyme_list[0] < 159:
		text = text + " " + rhyme_list[0]
		del rhyme_list[0]
	resp = twilio.twiml.Response()
	resp.sms(text)
	return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)