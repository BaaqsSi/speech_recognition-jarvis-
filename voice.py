
import speech_recognition as sr # xmis gasagebad
import time # current time gasagebad
from PIL import ImageGrab # image capturing isatvis
import cv2 # videos gaadasagebad (frame clipping type shi')
import numpy as np # aseve videostvis
import threading # threading rata vakontrolot videos ighebs tuara sanamde vakontrolebt stop vitkvit tuara (orivem ertad ro imushaos)
from win10toast import ToastNotifier # notification ebistvis
import AppOpener #app gasaxsnelad dasaxurad
import os #directory shesakmnelad
import spotipy#spotify api  gamosayeneblad
from spotipy.oauth2 import SpotifyOAuth#spotify authenticaciisatvis


CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URL = "http://localhost:8888/callback"
SCOPE = "user-library-read user-read-playback-state user-modify-playback-state"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URL,
    scope=SCOPE
))


def continue_music():
    sp.current_playback()

def pause_music():
    sp.pause_playback()

def next_msuic():
    sp.next_track()

def previous_music():
    sp.previous_track()



def play_song(music_name):
    result = sp.search(q=music_name,limit=1,type="track")

    if result["tracks"]["items"]:
        track = result["tracks"]["items"][0]
        track_id = track["id"]
        print(f"vrtav {track['name']} by {track['artists'][0]['name']}")

        devices = sp.devices()
        if devices["devices"]:
            device_id = devices["devices"][0]["id"]
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
        else:
            print("device ver ipova rom chartos musika")
    else:
        print("simghera ver ipova!")


#directory ebs ezebs screenshot,video ebis da tuar aris qmnis rata sheinaxos gadaghebuli videoebi da screenshotebi
def create_directories():
    base_dir = os.getcwd()
    screenshot_folder = os.path.join(base_dir, "screenshots")
    video_folder = os.path.join(base_dir, "videos")
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)
        print(f"sheiqmna folder: {screenshot_folder}")
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
        print(f"sheiqmna folder: {video_folder}")
    return screenshot_folder, video_folder

screenshot_folder, video_folder = create_directories()


# Global variablebi shesamowmeblad tu videos vighebt an thread midis (videos gadagheba)
stop_recording = False
recording_thread = None  

#videos gadagheba.. savedeba axlandeli drois saxelit rata videoebi ertmanets ar gadaeweros
def videogadagheba():
    global stop_recording

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_filename = os.path.join(video_folder,f'screen_record_{timestamp}.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    screen_width = 1920
    screen_height = 1080
    frame_rate = 20.0
    out = cv2.VideoWriter(output_filename, fourcc, frame_rate, (screen_width, screen_height))

    print("vigheb videos tkvi 'stop' shesachereblad..")
    while not stop_recording:
        # screenis capturing
        screenshot = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)

    # dasaveba sabolood roca stop_recording variable True gaxdeba
    out.release()
    cv2.destroyAllWindows()
    print(f"sheinaxa video aq: {output_filename}")

#screenshot gadagheba aris gaketebuli
def gadagheba():
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    filename = os.path.join(screenshot_folder,f"screenshot_of_{timestamp}.png")
    screenshot = ImageGrab.grab()
    screenshot.save(filename)
    print(f"sheinaxa video aq: {filename}")

#xmis gageba da chawera
def chasaweri(recognizer, microphone):
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return None
    except sr.WaitTimeoutError:
        print("xma ver gaigona timeout periodisas...")
        return None

#xmis mosmena da commandebis gageba ,amushaveba
def voice_listener(recognizer, microphone):
    global stop_recording, recording_thread
    toast = ToastNotifier()

    while True:
        command = chasaweri(recognizer, microphone)
        command = str(command)
        if command.startswith("jarvis"):
            command = command.replace("jarvis","")
            if command:
                print(f"command icno: {command}")
                #tu command udris 'record'-s arecordebs
                if "record" in command or "start recording" in command:
                    if recording_thread and recording_thread.is_alive():
                        toast.show_toast("Error", "ukve record mimdinareobs", duration=4)
                    else:
                        toast.show_toast("Screen Recorder", "Recording daiwyo... tkvi 'stop'rom gacherdes..", duration=4)
                        stop_recording = False
                        recording_thread = threading.Thread(target=videogadagheba)
                        recording_thread.start()
                #tu command udris 'stop'-s acherebs records
                elif "stop" in command or "turn off" in command:
                    if recording_thread and recording_thread.is_alive():
                        stop_recording = True
                        recording_thread.join()  # Wait for the thread to finish
                        toast.show_toast("Screen Recorder", "recording gacherda..", duration=4)
                    else:
                        toast.show_toast("Error", "recording ar mimdinareobs verafer gavacherebt...", duration=4)
                #tu command udris 'screenshots'-s ighebs screenshot-s
                elif "screenshot" in command or "take screenshot" in command:
                    toast.show_toast("Screenshot", "screenshot gadaigho..", duration=4)
                    gadagheba()
                #tu open udris commands  shemdeg moyolil sitkvas(aplikaciis saxels) ezebs pc-shi da xsnis tu ipova
                elif "open" in command:
                    new_command = command.split()
                    if "open" in new_command:
                        new_command.remove("open")
                    
                    if new_command:  # Ensure that new_command is not empty
                        try:
                            AppOpener.open("".join(new_command), match_closest=True)
                        except Exception as e:
                            print(f"error iyo aplikaciis gaxsnisas: {str(e)}")
                    else:
                        print("ar aris swore specified aplikacia gasaxsnelad")

                #tu open udris commands  shemdeg moyolil sitkvas(aplikaciis saxels) ezebs pc-shi da tishavs tu ipova rom gaxsnilia
                elif "close" in command:
                    new_command = command.split()
                    if "close" in new_command:
                        new_command.remove("close")
                    
                    if new_command: 
                        try:
                            AppOpener.close("".join(new_command), match_closest=True)
                        except Exception as e:
                            print(f"error iyo aplikaciis daxurvisas: {str(e)}")
                    else:
                        print("ar aris swore specified aplikacia dasaketat")


                elif "next" in command or "next song" in command:
                    next_msuic()

                elif "previous" in command or "pervious song" in command:
                    previous_music()


                if "play" in command:
                    song_name = command.replace("play", "").strip() 
                    
                    if song_name:

                        print(f"vcdilob rom chavrto: {song_name}")
                        play_song(song_name)

                    else:
                        toast.show_toast("Error", "simghera ver ipova rasac rtavdit'.", duration=4)

                elif "continue" in command or "continue msuic" in command:
                    continue_music()

                elif "pause" in command or "pause music" in command:
                    pause_music()
                

                elif "shutdown" in command:
                    print("itisheba jarvis... madloba gamoyenebisatvis..")
                    break

                else:
                    toast.show_toast("amocunobi command", "scade 'record', 'stop',  'screenshot','next', or 'previous'. ", duration=4)

            
        else:
            pass
            
def run_voice_listener():
    #sachiro racgebi speech_recognition isatvis
    r = sr.Recognizer()
    mic = sr.Microphone()
    r.energy_threshold = 400

    #gavushvat mtavari funckia
    voice_listener(r, mic)

#mtavari kodi
if __name__ == "__main__":
    #gavushvat  funckiashi motavsebuli mtavari funckiis thread

    voice_thread = threading.Thread(target=run_voice_listener)
    voice_thread.start()