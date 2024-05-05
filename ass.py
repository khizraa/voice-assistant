import pyaudio
import wave
import datetime
import speech_recognition as sr
from gtts import gTTS
import playsound
from pydub import AudioSegment
import webbrowser
import pyautogui
import wikipedia

tasks = []
listeningToTask = False

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None
    except sr.RequestError:
        print("Sorry, there was an error with the Google Speech Recognition API.")
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def respond(response_text):
    print(response_text)
    tts = gTTS(text=response_text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")

def record_audio(duration=5, chunk_size=1024, sample_format=pyaudio.paInt16, channels=1, sample_rate=44100):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=sample_format, channels=channels, rate=sample_rate, frames_per_buffer=chunk_size, input=True)
    print("Recording...")
    frames = []
    for _ in range(int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Finished recording.")
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"recorded_audio_{timestamp}.wav"
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(sample_format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved as {file_name}")
    return file_name

def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=1)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"DisambiguationError: {e}"
    except wikipedia.exceptions.PageError as e:
        return f"PageError: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_current_time():
    now = datetime.datetime.now()
    meridiem = "AM" if now.hour < 12 else "PM"
    hour = now.hour % 12
    if hour == 0:
        hour = 12
    minute = str(now.minute).zfill(2)
    time_str = f"It is {hour}:{minute} {meridiem}."
    return time_str

def get_current_date():
    now = datetime.datetime.now()
    date_str = now.strftime("Today is %A, %B %d, %Y.")
    return date_str

def main():
    global tasks
    global listeningToTask
    while True:
        command = listen_for_command()
        if command:
            if listeningToTask:
                tasks.append(command)
                listeningToTask = False
                respond("Adding " + command + " to your task list. You have " + str(len(tasks)) + " tasks currently in your list.")
            elif "add a task" in command:
                listeningToTask = True
                respond("Sure, what is the task?")
            elif "list tasks" in command:
                respond("Sure. Your tasks are:")
                for task in tasks:
                    respond(task)
            elif "take a screenshot" in command:
                pyautogui.screenshot("screenshot.png")
                respond("I took a screenshot for you.")
            elif "open youtube" in command:
                respond("Opening YouTube.")
                webbrowser.open("https://www.youtube.com/")
            elif "record audio" in command:   #Input: record audio
                respond("Starting audio recording. Speak now.")
                audio_file = record_audio()
                respond("Audio recording complete. ")
            elif "time" in command:      #Input: What is the time?
                time_str = get_current_time()
                respond(time_str)
            elif "date" in command or "today" in command:   #input: What is today's date?
                date_str = get_current_date()
                respond(date_str)
            elif any(word in command for word in ["who", "what", "how", "when", "where"]):    #Input: Who is __________?
                wiki_summary = search_wikipedia(command)
                respond(wiki_summary)
            elif "exit" in command:
                respond("Goodbye!")
                break
            else:
                respond("Sorry, I'm not sure how to handle that command.")

if __name__ == "__main__":
    main()
