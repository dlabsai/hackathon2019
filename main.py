#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tts import synthesize_text_with_audio_profile
from stts import listen_for_speech, stt_google_wav

from deeppavlov import configs, build_model

import stringdist
import re
import googlemaps
from datetime import datetime
from datetime import timedelta
from datetime import datetime

def get_info():
    text_start = 'Proszę, podaj mi swoje imie i nazwisko'
    flag_finish = False
    while not flag_finish:
        synthesize_text_with_audio_profile(text_start)
        listen_for_speech(4)
        result = stt_google_wav('output.wav')  # translate audio file
        text, flag_finish, flag_stage = main(result)
        print(text, flag_finish, flag_stage)
        if flag_stage is False:
            count = 0
            while count <=2:
                synthesize_text_with_audio_profile(text)
                listen_for_speech(3)
                result = stt_google_wav('output.wav')
                count+=1
                text, flag_finish, flag_stage = main(result)
                if flag_stage:
                    break
        text_start = text
    synthesize_text_with_audio_profile(text_start)
#        RETRY_COUNT += 1
#        if RETRY_COUNT == 3:
#           synthesize_text_with_audio_profile('Chyba nie mogę Ci pomóc, przekieruje Naszą rozmowe do innego konsultanta')
#           return ""
#       

def get_event(input_text, interesting_list_word):
    deep_pavlov_prepro = ner_model([input_text])
    # print(deep_pavlov_prepro)
    list_words = deep_pavlov_prepro[0][0]
    list_predict = deep_pavlov_prepro[1][0]
    list_word_predict = list(zip(list_words, list_predict))
    list_name = [i for i, k in list_word_predict if k in interesting_list_word]
    if len(list_name) > 0:
        status = True
    else:
        status = False
    return status, list_name


def check_pesel(pesel):
    # Sprawdzanie regexpem
    if (re.match('[0-9]{11}$', pesel)):
        pass
    else:
        return 0
    # Sprawdzenie sumy kontrolnej...
    l = int(pesel[10])
    suma = ((l * int(pesel[0])) + (3 * int(pesel[l])) + (7 * int(pesel[2])) + (9 * int(pesel[3])) + (
    (l * int(pesel[4]))) + (3 * int(pesel[5])) + (7 * int(pesel[6])) + (9 * int(pesel[7])) + (l * int(pesel[8])) + (
                        3 * int(pesel[9])))
    kontrolka = 10 - (suma % 10)
    if kontrolka == 10:
        kontrolka = 0
    else:
        kontrolka = kontrolka
    # kontrolka i sprawdzenie zgodnosci
    if ((kontrolka == 10) or (kontrolka == 0)):
        return False
    else:
        return True


def pesel_veryfication(pesel):
    print(pesel)
    pesel = pesel.strip()
    if check_pesel(pesel):
        return True, pesel
    else:
        return False, pesel


def get_doctor_job(input_text, LIST_SPECIALITY_NAME):
    input_text = input_text.strip().lower()
    list_values_lev = [stringdist.levenshtein(input_text, spec) for spec in LIST_SPECIALITY_NAME]
    min_dist = min(list_values_lev)
    if min_dist < 5:
        return True, LIST_SPECIALITY_NAME[list_values_lev.index(min_dist)]
    else:
        return False, LIST_SPECIALITY_NAME[list_values_lev.index(min_dist)]


def google_standarization(adress_input_text, GEO_LIST):
    stat, addres = get_event(adress_input_text, GEO_LIST)
    if stat:
        addres = ' '.join(addres)
        gmaps = googlemaps.Client(key='')
        # Geocoding an address
        final = {}
        geocode_result = gmaps.geocode(adress_input_text)
        data = geocode_result[0]
        for item in data["address_components"]:
            for category in item["types"]:
                data[category] = {}
                data[category] = item["long_name"]
        final["street"] = data.get("route", None)
        final["city"] = data.get("locality", None)
        if final["city"] is not None and final["street"] is not None:
            return True, {"street": final["street"], "city": final["city"]}
        else:
            return False, None
    else:
        return False, None


def get_date(input_text):
    day, month = input_text.split()
    months_dict = {
        "stycznia": 1,
        "lutego": 2,
        "marca": 3,
        "kwietnia": 4,
        "maja": 5,
        "czerwca": 6,
        "lipca": 7,
        "sierpnia": 8,
        "września": 9,
        "października": 10,
        "listopada": 11,
        "grudnia": 12
    }
    if input_text == "jutro":
        data = (datetime.now() + timedelta(days=1)).date()
        return (data)
    mies = months_dict[month]
    year = 2019
    day = int(day)
    return datetime(year, mies, day).date()


def get_free_appoitm(prefered_date, param):
    first_free = param[0]
    date_list = param[1]
    stat, prefered_date = get_event(prefered_date, date_list)
    if stat:
        prefered_date = ' '.join(prefered_date)
        prefered_date = get_date(prefered_date)
        first_free = get_date(first_free)
        if prefered_date > first_free:
            return True, prefered_date
        return False, first_free
    else:
        return False, None


def gener_final_text(sumarize_text):
    name = ' '.join(sumarize_text["get_name"])
    diag = sumarize_text['get_specjality']
    address = sumarize_text["get_address"]
    street = address["street"]
    city = address["city"]
    data = sumarize_text["get_date"]
    months_dict = {
        "stycznia": 1,
        "lutego": 2,
        "marca": 3,
        "kwietnia": 4,
        "maja": 5,
        "czerwca": 6,
        "lipca": 7,
        "sierpnia": 8,
        "września": 9,
        "października": 10,
        "listopada": 11,
        "grudnia": 12
    }
    for key, value in months_dict.items():
        if value == data.month:
            month = key
    day = data.day
    return "Dziękuję za informację! Dla pewności powtórzę- pan %s został umówiony na %s przy ulicy %s w %s %s %s. Do zobaczenia!" % (
    name, diag, street, city, day, month)



TIME = ['B-TIME', 'I-TIME']
DATE = ['B-DATE', 'I-DATE']
PERSON = ['B-PERSON', 'I-PERSON']
GEO_LIST = ['B-GPE']
FREE_DATE = "15 listopada"
LIST_SPECIALITY_NAME = ['prądy', 'laser', 'ultradźwięki', 'krioterapia', 'usg jamy brzusznej', 'usg sutka']

status_dict = {"get_name": False, 
               #"get_pesel": False,
               "get_specjality": False, "get_address": False, "get_date": False}
dict_functions = {"get_name": get_event, "get_pesel": pesel_veryfication, "get_specjality": get_doctor_job,
                  "get_address": google_standarization, "get_date": get_free_appoitm}
dict_params = {"get_name": PERSON, 
               #"get_pesel": None, 
               "get_specjality": LIST_SPECIALITY_NAME,
               "get_address": GEO_LIST, "get_date": [FREE_DATE, TIME + DATE]}

quest_stage = {"get_name": "Proszę powiedzieć swoje imię i nazwisko.",
              # "get_pesel": "Proszę podać swój numer PESEL.",
               "get_specjality": "Na jaką diagnozę chcę Pan się umówić?",
               "get_address": "Do jakiej placówki chce przyjść Pan?",
               "get_date": "Jaki Panu odpowiada termin?"}
sumarize_text = {"get_name": None,
                # "get_pesel": None,
                 "get_specjality": None,
                 "get_address": None,
                 "get_date": None}
quest_repeat = {"get_name": "Proszę powtórzyć jeszcze raz",
               # "get_pesel": "Proszę spróbować jeszcze raz",
                "get_specjality": "nie przeprowadzamy takich diagnostyk, proszę jeszcze raz",
                "get_address": "Proszę spróbować jeszcze raz",
                "get_date": "Proszę podać inny termin bo ten jest zajęty"}




# ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)

def welcome():
    synthesize_text_with_audio_profile('Cześć, jestem Alicja z Medicover!')
    synthesize_text_with_audio_profile('Jestem tu po to, aby umówić Cię na wizyte')
    


def main(input_text):
    keyList = list(status_dict.keys())
    print(keyList)
    for i, key in enumerate(keyList):
        
        status_current = status_dict[key]
        print(status_current)
        if not status_current:
            param = dict_params[key]
            if param is not None:
                status_fun, event = dict_functions[key](input_text, param)
            else:
                status_fun, event = dict_functions[key](input_text)
            if status_fun:
                status_dict[key] = status_fun
                sumarize_text[key] = event
                print(event)
                if i < len(keyList) - 1:
                    return ("Dziękuję! " + quest_stage[keyList[i + 1]], False, True)
                else:
                    if all(value == True for value in status_dict.values()):
                        return (gener_final_text(sumarize_text), True, True)
            else:
                return quest_repeat[key], False, False
        else:
            continue


#name_test = "Dzień dobry! Nazywam się Adrian Nowak."
#pesel_test = "84071429849"
#doctor_test = 'ultradzwiek'
#adress_test = "Warszawa Pulawska"
#date_test = "Chciałbym się umówić na wizytę do diagnostyke na 31 grudnia"

#main(name_test)
#main(pesel_test)
#main(doctor_test)
#main(adress_test)
#main(date_test)

if(__name__ == '__main__'):

    ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=False)
    response = ""
    welcome()
    get_info()
    
    
    
    
            