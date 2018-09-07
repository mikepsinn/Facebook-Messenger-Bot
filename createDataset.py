import pandas as pd
import numpy as np
import dateparser
import os
import re
from datetime import datetime

# personName = raw_input('Enter your full name: ')
personName = "Mike P. Sinn"
fbData = 'n'
# fbData = raw_input('Do you have Facebook data to parse through (y/n)?')
# googleData = raw_input('Do you have Google Hangouts data to parse through (y/n)?')
googleData = 'y'
# linkedInData = raw_input('Do you have LinkedIn data to parse through (y/n)?')
linkedInData = 'y'
whatsAppData = 'n'


# whatsAppData = raw_input('Do you have whatsAppData to parse through (y/n)?')


def getWhatsAppData():
    df = pd.read_csv('whatsapp_chats.csv')
    response_dictionary = dict()
    received_messages = df[df['From'] != personName]
    sent_messages = df[df['From'] == personName]
    combined = pd.concat([sent_messages, received_messages])
    other_persons_message, my_message = "", ""
    first_message = True
    for index, row in combined.iterrows():
        if row['From'] != personName:
            if my_message and other_persons_message:
                other_persons_message = cleanMessage(other_persons_message)
                my_message = cleanMessage(my_message)
                response_dictionary[other_persons_message.rstrip()] = my_message.rstrip()
                other_persons_message, my_message = "", ""
            other_persons_message = other_persons_message + str(row['Content']) + " "
        else:
            if first_message:
                first_message = False
                # Don't include if I am the person initiating the convo
                continue
            my_message = my_message + str(row['Content']) + " "
    return response_dictionary


def getGoogleHangoutsData():
    # Putting all the file names in a list
    all_files = []
    # Edit these file and directory names if you have them saved somewhere else
    for filename in os.listdir('GoogleTextForm'):
        if filename.endswith(".txt"):
            all_files.append('GoogleTextForm/' + filename)

    response_dictionary = dict()  # The key is the other person's message, and the value is my response
    # Going through each file, and recording everyone's messages to me, and my responses
    for currentFile in all_files:
        my_message, other_persons_message, current_speaker = "", "", ""
        opened_file = open(currentFile, 'r')
        all_lines = opened_file.readlines()
        for index, lines in enumerate(all_lines):
            # The sender's name is separated by < and >
            left_bracket = lines.find('<')
            right_bracket = lines.find('>')

            # Find messages that I sent
            if lines[left_bracket + 1:right_bracket] == personName:
                if not my_message:
                    # Want to find the first message that I send (if I send multiple in a row)
                    startMessageIndex = index - 1
                my_message += lines[right_bracket + 1:]

            elif my_message:
                # Now go and see what message the other person sent by looking at previous messages
                for counter in range(startMessageIndex, 0, -1):
                    currentLine = all_lines[counter]
                    # In case the message above isn't in the right format
                    if currentLine.find('<') < 0 or currentLine.find('>') < 0:
                        my_message, other_persons_message, current_speaker = "", "", ""
                        break
                    if not current_speaker:
                        # The first speaker not named me
                        current_speaker = currentLine[currentLine.find('<') + 1:currentLine.find('>')]
                    elif current_speaker != currentLine[currentLine.find('<') + 1:currentLine.find('>')]:
                        # A different person started speaking, so now I know that the first person's message is done
                        other_persons_message = cleanMessage(other_persons_message)
                        my_message = cleanMessage(my_message)
                        response_dictionary[other_persons_message] = my_message
                        break
                    other_persons_message = currentLine[currentLine.find('>') + 1:] + other_persons_message
                my_message, other_persons_message, current_speaker = "", "", ""
    return response_dictionary


def getFacebookData():
    responseDictionary = dict()
    fbFile = open('fbMessages.txt', 'r')
    allLines = fbFile.readlines()
    myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
    for index, lines in enumerate(allLines):
        rightBracket = lines.find(']') + 2
        justMessage = lines[rightBracket:]
        colon = justMessage.find(':')
        # Find messages that I sent
        if justMessage[:colon] == personName:
            if not myMessage:
                # Want to find the first message that I send (if I send multiple in a row)
                startMessageIndex = index - 1
            myMessage += justMessage[colon + 2:]

        elif myMessage:
            # Now go and see what message the other person sent by looking at previous messages
            for counter in range(startMessageIndex, 0, -1):
                currentLine = allLines[counter]
                rightBracket = currentLine.find(']') + 2
                justMessage = currentLine[rightBracket:]
                colon = justMessage.find(':')
                if not currentSpeaker:
                    # The first speaker not named me
                    currentSpeaker = justMessage[:colon]
                elif currentSpeaker != justMessage[:colon] and otherPersonsMessage:
                    # A different person started speaking, so now I know that the first person's message is done
                    otherPersonsMessage = cleanMessage(otherPersonsMessage)
                    myMessage = cleanMessage(myMessage)
                    responseDictionary[otherPersonsMessage] = myMessage
                    break
                otherPersonsMessage = justMessage[colon + 2:] + otherPersonsMessage
            myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
    return responseDictionary


def getLinkedInData():
    df = pd.read_csv('Inbox.csv')
    # dateTimeConverter = lambda x: datetime.strptime(x, '%B %d, %Y, %I:%M %p')
    date_time_converter = lambda x: dateparser.parse(x)
    responseDictionary = dict()
    peopleContacted = df['From'].unique().tolist()
    for person in peopleContacted:
        receivedMessages = df[df['From'] == person]
        sentMessages = df[df['To'] == person]
        if len(sentMessages) == 0 or len(receivedMessages) == 0:
            # There was no actual conversation
            continue
        combined = pd.concat([sentMessages, receivedMessages])
        combined['Date'] = combined['Date'].apply(date_time_converter)
        combined = combined.sort(['Date'])
        other_persons_message, my_message = "", ""
        first_message = True
        for index, row in combined.iterrows():
            if row['From'] != personName:
                if my_message and other_persons_message:
                    other_persons_message = cleanMessage(other_persons_message)
                    my_message = cleanMessage(my_message)
                    responseDictionary[other_persons_message.rstrip()] = my_message.rstrip()
                    other_persons_message, my_message = "", ""
                if isinstance(row['Content'], basestring):
                    other_persons_message = other_persons_message + row['Content'] + " "
            else:
                if first_message:
                    first_message = False
                    # Don't include if I am the person initiating the convo
                    continue
                my_message = my_message + str(row['Content']) + " "
    return responseDictionary


def cleanMessage(message):
    # Remove new lines within message
    cleaned_message = message.replace('\n', ' ').lower()
    # Deal with some weird tokens
    cleaned_message = cleaned_message.replace("\xc2\xa0", "")
    # Remove punctuation
    cleaned_message = re.sub('([.,!?])', '', cleaned_message)
    # Remove multiple spaces in message
    cleaned_message = re.sub(' +', ' ', cleaned_message)
    return cleaned_message


combinedDictionary = {}
if googleData == 'y':
    print 'Getting Google Hangout Data'
    combinedDictionary.update(getGoogleHangoutsData())
if fbData == 'y':
    print 'Getting Facebook Data'
    combinedDictionary.update(getFacebookData())
if linkedInData == 'y':
    print 'Getting LinkedIn Data'
    combinedDictionary.update(getLinkedInData())
if whatsAppData == 'y':
    print 'Getting whatsApp Data'
    combinedDictionary.update(getWhatsAppData())
print 'Total len of dictionary', len(combinedDictionary)

print 'Saving conversation data dictionary'
np.save('conversationDictionary.npy', combinedDictionary)

conversationFile = open('conversationData.txt', 'w')
for key, value in combinedDictionary.iteritems():
    if not key.strip() or not value.strip():
        # If there are empty strings
        continue
    conversationFile.write(key.strip() + value.strip())
