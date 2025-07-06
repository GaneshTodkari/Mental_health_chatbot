from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from textblob import TextBlob
import random
import re


class ActionDetectEmotion(Action):
    def name(self) -> str:
        return "action_detect_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        raw_text = tracker.latest_message.get('text', '')
        corrected_text = str(TextBlob(raw_text.lower()).correct())

        # 🚨 Crisis check
        crisis_phrases = [
            "kill myself", "want to die", "end my life", "commit suicide",
            "suicide", "leaving this world", "life is not worth living", "i hate my life"
        ]
        for phrase in crisis_phrases:
            if re.search(r'\b' + re.escape(phrase) + r'\b', corrected_text):
                dispatcher.utter_message(
                    text="""
                I'm really sorry you're feeling this way. You're not alone.

                If you're in danger or need to talk to someone urgently, please reach out to AASRA:
                📞 AASRA Helpline: +91-9820466726
                🌐 Website: [www.aasra.info](http://www.aasra.info)

                I'm here for you too. Would you like to talk more?
                """,
                    custom={"emotion": "crisis"}
                )
                return [SlotSet("last_emotion", "crisis")]

        # Emotion detection by keyword and sentiment
        emotion_keywords = {
            'happy': ['happy', 'better', 'joy', 'joyful', 'excited', 'great', 'good', 'awesome', 'amazing'],
            'sad': ['sad', 'unhappy', 'depressed', 'cry', 'down', 'worthless', 'hopeless', 'nothing matters'],
            'angry': ['angry', 'mad', 'furious', 'irritated'],
            'anxious': ['anxious', 'nervous', 'worried', 'tense'],
            'lonely': ['lonely', 'alone', 'isolated', 'ignored'],
            'stressed': ['stressed', 'overwhelmed', 'tired', 'exhausted', 'burned out'],
        }

        emotion_responses = {
            'happy': ["That's great to hear! 😊 What made you feel happy today?"],
            'sad': ["I'm sorry you're feeling sad. Want to talk about it?"],
            'angry': ["It's okay to feel angry. Want to share what's upsetting you?"],
            'anxious': ["That sounds tough. Want to talk through it?"],
            'lonely': ["You’re not alone. Want to share what’s been happening?"],
            'stressed': ["That sounds overwhelming. Want to talk about what's causing this stress?"],
            'neutral': ["I’m here for you. What would you like to talk about?"]
        }

        # Determine emotion
        detected_emotion = "neutral"
        for emotion, keywords in emotion_keywords.items():
            for word in keywords:
                if re.search(r'\b' + re.escape(word) + r'\b', corrected_text):
                    detected_emotion = emotion
                    break
            if detected_emotion != "neutral":
                break

        # Fallback to sentiment
        sentiment_score = TextBlob(corrected_text).sentiment.polarity
        if detected_emotion == "neutral":
            if sentiment_score > 0.2:
                detected_emotion = "happy"
            elif sentiment_score < -0.2:
                detected_emotion = "sad"
        print(f'🔍 Detected emotion: {detected_emotion} ')

        dispatcher.utter_message(
            text=random.choice(emotion_responses.get(detected_emotion, ["I'm here to listen."])),
            custom={"emotion": detected_emotion}
        )
        print(f"📤 Sending emotion: {detected_emotion}")
        return [SlotSet("last_emotion", detected_emotion)]


class ActionSadAffirmResponse(Action):
    def name(self) -> Text:
        return "action_sad_affirm_response"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="I'm here for you. Do you want to talk more about what's making you feel this way? 💙"
        )
        return []


class ActionAngryDenyResponse(Action):
    def name(self) -> Text:
        return "action_angry_deny_response"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="That's okay. If you're not ready to talk, I respect that. Just know I'm here when you are. 🔥"
        )
        return []


class ActionRespondToAffirmOrDeny(Action):
    def name(self) -> Text:
        return "action_handle_affirm_deny"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message['intent'].get('name')
        last_emotion = tracker.get_slot("last_emotion")

        if last_emotion in ['stressed', 'sad', 'angry', 'anxious', 'lonely']:
            if intent == "affirm":
                dispatcher.utter_message(text="I'm here. You can tell me more when you're ready.")
            elif intent == "deny":
                dispatcher.utter_message(text="That’s okay. Just know I’m always here for you.")

        elif last_emotion == "happy":
            if intent == "affirm":
                dispatcher.utter_message(text="That’s awesome! Let’s keep the positivity going! 😊")
            elif intent == "deny":
                dispatcher.utter_message(text="No worries. You can tell me whenever you feel like sharing.")

        elif last_emotion == "crisis":
            dispatcher.utter_message(text="Please don’t hesitate to reach out to someone. You're not alone.")

        else:
            dispatcher.utter_message(text="Okay, I'm here if you need me.")

        return []
