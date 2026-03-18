import pyttsx3
import speech_recognition as sr
from translate import Translator

def speak(text, language):
    print(f"{text}")

    tts = pyttsx3.init()
    voices = tts.getProperty("voices")
    pl_voice_id = None
    en_voice_id = None

    for v in voices:
        name_lower = v.name.lower()
        if "polish" in name_lower:
            pl_voice_id = v.id
        if "english" in name_lower:
            en_voice_id = v.id

    if en_voice_id is None and voices:
        en_voice_id = voices[0].id
    if pl_voice_id is None and voices:
        pl_voice_id = voices[0].id

    if language == "pl":
        tts.setProperty("voice", pl_voice_id)
    else:
        tts.setProperty("voice", en_voice_id)

    tts.say(text)
    tts.runAndWait()

def listen(language):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source)
    except OSError:
        print(f"Problem z rozpoznawaniem mowy: Nie wykryto mikrofonu")
        return None

    try:
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Problem z rozpoznawaniem mowy: {e}")
        return None

def translate(text, from_language, to_language):
    try:
        translator = Translator(from_lang=from_language, to_lang=to_language)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Nie udało się przetłumaczyć tekstu: {e}")
        return None

def ask_for_language():
    speak("Powiedz polski lub angielski, aby wybrać język", "pl")
    speak("Say polish or english to choose language", "en")
    text = listen("pl-PL")

    if text is None:
        text = listen("en-US")
        if text is None:
            return None

    text_lower = text.lower().strip()

    if any(w in text_lower for w in ["polski", "polish"]):
        return "pl"
    if any(w in text_lower for w in ["angielski", "english"]):
        return "en"
    if any(w in text_lower for w in ["bywaj", "good bye", "goodbye"]):
        return "quit"

    return None

def translation_loop(language):
    if language == "pl":
        from_language, to_language = "pl", "en"
        listen_language = "pl-PL"
    else:
        from_language, to_language = "en", "pl"
        listen_language = "en-US"

    info_pl = "Tryb: Polski na Angielski. Mów, a przetłumaczę. Powiedz 'zmień język' lub 'bywaj', aby zakończyć"
    info_en = "Mode: English to Polish. Speak and I'll translate. Say 'change language' or 'goodbye' to exit"
    info = info_pl if language == "pl" else info_en
    speak(info, language)

    while True:
        text = listen(listen_language)

        if text is None:
            not_understood_pl = "Nie zrozumiałem, spróbuj ponownie"
            not_understood_en = "I didn't understand, please try again"
            msg_not_understood = not_understood_pl if language == "pl" else not_understood_en
            speak(msg_not_understood, language)
            continue

        text_lower = text.lower().strip()
        print(f"Rozpoznano: {text}")

        if any(w in text_lower for w in ["bywaj", "good bye", "goodbye"]):
            return "quit"

        if any(w in text_lower for w in ["zmień język", "change language"]):
            return "switch"

        translated = translate(text, from_language, to_language)
        if translated is None:
            err_pl = "Błąd tłumaczenia, spróbuj ponownie"
            err_en = "Translation error, please try again"
            err = err_pl if language == "pl" else err_en
            speak(err, language)
            continue

        speak(translated, to_language)

def main():
    selected_language = None

    while True:
        if selected_language is None:
            choice = ask_for_language()
            if choice is None:
                speak("Nie rozpoznano wybranego języka", "pl")
                speak("Selected language wasn't recognized", "en")
                continue
            elif choice == "quit":
                break
            selected_language = choice

        result = translation_loop(selected_language)
        if result == "quit":
            break
        elif result == "switch":
            selected_language = None

    speak("Bywaj", "pl")
    speak("Goodbye", "en")

if __name__ == '__main__':
    main()