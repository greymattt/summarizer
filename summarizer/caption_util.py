import requests
import youtube_dl

auth_key = "10af5eedc9394a968ecec5f4fe153bcc" # os.environ["ASSEMBLY_API_TOKEN"]
# url = "https://www.youtube.com/watch?v=mC2DwdfA62E" # takes around 2 minutes
# url = "https://www.youtube.com/watch?v=a7_WFUlFS94" # 30 seconds to download, only 1 chp
# url = "https://www.youtube.com/watch?v=kdvVwGrV7ec" # took
url = "https://www.youtube.com/watch?v=lGx7oeiIlLM" # decent, best bet.

# ydl options
ydl_opts = {
   'format': 'bestaudio/best',
   'postprocessors': [{
       'key': 'FFmpegExtractAudio',
       'preferredcodec': 'mp3',
       'preferredquality': '192',
   }],
   'ffmpeg-location': './',
   'outtmpl': "./%(id)s.%(ext)s",
}

# download yt file
def download_from_yt(url):
    def get_extracted_info():
        link = url.strip()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(link)
    meta = get_extracted_info()
    save_location = meta['id'] + ".mp3"
    duration = meta['duration']
    print('Saved mp3 to', save_location)

    return (save_location, duration)

# to be used for uplaoding
def read_file_data(file):
    CHUNK_SIZE = 5242880

    with open(file, 'rb') as _file:
        while True:
            data = _file.read(CHUNK_SIZE)
            if not data:
                break
            yield data

# upload the file to assemblyai
def upload_file(save_location):
    # save_location = download_from_yt(url)
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'authorization': auth_key
    }

    # upload to the assemblyapi
    upload_response = requests.post(
        upload_endpoint,
        headers=headers, data=read_file_data(save_location)
    )

    audio_url = upload_response.json()['upload_url']
    print('Uploaded to', audio_url)

    return audio_url

# process the audio url and get its id
def process_url_id(audio_url):
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": auth_key,
        "content-type": "application/json"
    }

    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': True
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']

# get the processed data
def getProcessedData(id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{id}"
    headers = {
        "authorization": auth_key,
    }

    # do-while to get the chapters once the video has been processed
    while True:
        response = requests.get(endpoint, headers=headers).json()
        if response['status'] == 'completed':
            return response

# get the whole transcript
def getTranscript(id):
    return getProcessedData(id)['text']

# get the actual chapters
def getChapters(id):
    return getProcessedData(id)['chapters']

# the whole thing bundled
def getChaptersFrom(url):
    save_location, duration = download_from_yt(url)
    print(duration*2/5, 'seconds')

    audio_url = upload_file(save_location)
    audio_id = process_url_id(audio_url)
    return getChapters(audio_id)

def main(url):
    print(getChaptersFrom(url))

# run for tests
