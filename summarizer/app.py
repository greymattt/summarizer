# this is the server of the app.
# it facilitates connections to the database? and the Machine Learning components
from caption_util import *
from flask import Flask, request
import json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
from time import sleep
import threading

# dictionary of the url to the actual chapter, transcripts, and save locations
chapters = {}
transcripts = {}
save_locations = {}
audio_ids = {}

# temporary for each request
save_location, duration = '', 0

def processing_download(url):
    global save_location, duration, save_locations
    save_location, duration = download_from_yt(url)
    duration = duration*2/5
    save_locations[url] = save_location

# second temporary    
audio_id = ''

def process_audio_captioning(url):
    global audio_id, audio_urls
    audio_url = upload_file(save_locations[url])
    audio_id = process_url_id(audio_url)
    audio_ids[url] = audio_id

# getting captions -- third temp
captions = {}

def get_captions_load(url):
    global audio_ids, captions
    
    if not url in audio_ids:
        return json.dumps({'s':2})
    
    id = audio_ids[url]
    chps = getChapters(id)
    captions = chps


# starts processing the url and returns the time needed
@app.route("/process_url", methods=['POST'])
@cross_origin()
def process_url():
    url = request.get_json()['url']
    if url in save_locations:
        thread = threading.Thread(target=get_captions_load(url))
        thread.start()
        return json.dumps({'saved':save_location, 'duration': 1,'cached':True,'infos':captions})

    thread = threading.Thread(target=processing_download(url))
    thread.start()
    print(url)
    
    # start the captioning process -> takes 'duration' seconds to complete
    # as a side effect
    process_audio_captioning(url)
    
    # how to do the asynchronous action here
    doc = {'duration':duration, 'cached':False} # duration to get captions
    return json.dumps(doc) # return it


@app.route("/get_captions", methods=['POST'])
@cross_origin()
def get_captions():
    url = request.get_json()['url']
    thread = threading.Thread(target=get_captions_load(url))
    thread.start()
    
    # how to do the asynchronous action here
    global captions
    return json.dumps({'chapters':captions}) # return it
    
    
    
    
    
    
if __name__ == '__main__':
	app.run(debug=True)
