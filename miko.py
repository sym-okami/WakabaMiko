import sqlite3
from datetime import datetime
import sys
import random
sys.path.append('../GetterCore')
import gettercore

class Miko(gettercore.GetterCore):
    def __init__(self, user, oauth):
        gettercore.GetterCore.__init__(self, user, oauth)
        self.conn = sqlite3.connect('miko.db', check_same_thread = False)
        self.setup_db()
    
    def setup_db(self):
        c = self.conn.cursor()
        # create the virtue table
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table'" + \
            "AND name='virtue'")
        if c.fetchone()[0] != 1:
            c.execute("CREATE TABLE virtue (username text, virtue integer)")
        
        # create the faith table
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table'" + \
            "AND name='faith'")
        if c.fetchone()[0] != 1:
            c.execute("CREATE TABLE faith (date text, faith integer)")

        self.conn.commit()

    def add_virtuous_soul(self, username):
        c = self.conn.cursor()
        c.execute("SELECT EXISTS(SELECT 1 FROM virtue WHERE username='{}')".
        format(username))
        if c.fetchone()[0] == 0:
            # user isn't in db yet
            c.execute("INSERT INTO virtue VALUES('{}',0)".format(username))
            self.conn.commit()

    def change_virtue(self, username, modifier):
        self.add_virtuous_soul(username)
        current_virtue = self.get_virtue(username)
        c = self.conn.cursor()
        c.execute("UPDATE virtue SET virtue={} WHERE username='{}'".format(
            current_virtue + modifier, username
        ))
        self.conn.commit()

    def get_virtue(self, username):
        c = self.conn.cursor()
        self.add_virtuous_soul(username)
        c.execute("SELECT virtue FROM virtue WHERE username='{}'".
        format(username))
        return c.fetchone()[0]

    def get_date(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    def create_day_of_worship(self):
        c = self.conn.cursor()
        date = self.get_date()
        c.execute("SELECT EXISTS(SELECT 1 FROM faith WHERE date='{}')".format(
            date))
        if c.fetchone()[0] == 0:
            # user isn't in db yet
            c.execute("INSERT INTO faith VALUES('{}',0)".format(date))
            self.conn.commit()

    def update_faith(self, value):
        today = self.get_date()
        todays_faith = self.get_faith(today)
        c = self.conn.cursor()
        c.execute("UPDATE faith SET faith={} WHERE date='{}'".format(
            todays_faith + value, today))
        self.conn.commit()

    def get_faith(self, date):
        self.create_day_of_worship()
        c = self.conn.cursor()
        c.execute("SELECT faith FROM faith WHERE date='{}'".format(date))
        return c.fetchone()[0]

    def get_total_faith(self):
        self.create_day_of_worship()
        c = self.conn.cursor()
        c.execute("SELECT SUM(faith) FROM faith")
        return c.fetchone()[0]

    def get_days_of_prayer(self):
        self.create_day_of_worship()
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM faith")
        return c.fetchone()[0]

    def todays_faith_message(self):
        faith = self.get_faith(self.get_date())
        if faith < 0:
            return "Oh, this is awful...what should we do? It seems no one has faith..."
        elif faith < 50:
            return "Ah...we've gathered some, but..."
        elif faith < 100:
            return "Our faith is growing stronger. Isn't that nice?"
        elif faith < 200:
            return "It seems there are plenty of faithful! How wonderful!"
        else:
            return "Truly, the Gods are pleased!"
        
    def total_faith_message(self):
        faith = self.get_total_faith()
        days = self.get_days_of_prayer()
        if days < 2:
            return "It is only the first day of prayer. Let us first see how the day ends."
        elif faith > 10000:
            return "We've hit a milestone of faith! Surely, we'll be rewarded."
        elif faith < 0:
            return "..."
        elif faith < 50*days:
            return "Day by day, we struggle to gather faith..."
        elif faith < 100*days:
            return "We're slowly gathering faith. I'm excited for the future!"
        elif faith < 200*days:
            return "Such bountiful faith!"
        else:
            return "Our prayers have reached the Gods!"

    def virtue_message(self, username):
        virtue = self.get_virtue(username)
        if virtue < 0:
            return "The Gods punish those who sin."
        elif virtue < 10:
            return "You must work harder! I believe in you."
        elif virtue < 30:
            return "Your good deeds are being recognized. Keep striving and you shall be rewarded."
        elif virtue < 50:
            return "How outstanding! All should strive to be like you."
        elif virtue < 100:
            return "The good do not claim to be good; rather, it is others that claim them to be good. Truly, you are someone I would be proud to call as such."
        else:
            return "I am blinded by your virtuous light!"

    def calculate_blessing(self, username):
        total_faith = self.get_total_faith()
        todays_faith = self.get_faith(self.get_date())
        days = self.get_days_of_prayer()
        if days < 2:
            average_faith = todays_faith
        else:
            average_faith = total_faith/days
        virtue = self.get_virtue(username)
        blessings = {"top": "http://how.moe/b/aIV.png",
        "mid-high": "http://how.moe/b/fCq.png",
        "mid-low": "http://how.moe/b/LTQ.png",
        "low": "http://how.moe/b/wuL.png"}
        # lower than average faith means it's harder to get a good blessing
        # this can be compensated with virtue
        virtue_mod = 0
        if virtue < 0:
            virtue_mod = 0
        elif virtue < 10:
            virtue_mod = 0.40 + 0.1*(virtue/10) # up to 0.5
        elif virtue < 30:
            virtue_mod = 0.5 + 0.25*(virtue/30) # up to 0.75
        elif virtue < 50:
            virtue_mod = 0.75 + 0.15*(virtue/50) # up to 0.9
        elif virtue < 100:
            virtue_mod = 0.9 + 0.1*(virtue/100) # up to 1
        else: 
            virtue_mod = virtue/100 # 1 and above

        blessing_chance = (todays_faith/average_faith)*virtue_mod
        if total_faith < 0 or todays_faith < 0 or virtue < 0:
            return blessings["low"]
        elif blessing_chance > 1:
            return blessings["top"]
        elif blessing_chance > 0.5:
            return blessings["mid-high"]
        elif blessing_chance > 0.2:
            return blessings["mid-low"]
        else:
            return blessings["low"]

    def on_mention(self, user_message, username, channel):
        responses_low_virtue = ["Ah...{}.", "@{} Perhaps you should consider praying today?",
        "{}, you must work harder.", "@{} Why are you here?", "@{} ..."]
        possible_responses = ["Hello, {}. Are you here to pray?", "{}, nice to see you.",
        "Do you need something, {}?", "@{} Yes, hello to you too.", "Hello, {}."]
        responses_high_virtue = ["Ah, {}! How wonderful to see you again!", "{} I missed you!",
        "{}, would you like to pray together?", "It's always a pleasure to see you, {}.",
        "@{} Is there anything you need? If so, please do not hesitate to ask me."]
        virtue = self.get_virtue(username)
        if virtue < 0:
            msg = random.choice(responses_low_virtue).format(username)
            self.send_msg(msg, channel)
        elif virtue < 100:
            msg = random.choice(possible_responses).format(username)
            self.send_msg(msg, channel)
        else:
            msg = random.choice(responses_high_virtue).format(username)
            self.send_msg(msg, channel)

    def run_command(self, user_message, username, channel):
        commands = ["!services", "!checkfaith", "!totalfaith", "!checkvirtue",
        "!blessing"]
        command = user_message[1:]

        if command.startswith("services"):
            self.send_msg("@{} Here are the services offered at this shrine: {}".
            format(username, str(commands)[1:-1]), channel)

        elif command.startswith("checkfaith"):
            self.send_msg(self.todays_faith_message(), channel)

        elif command.startswith("totalfaith"):
            self.send_msg(self.total_faith_message(), channel)

        elif command.startswith("checkvirtue"):
            self.send_msg(self.virtue_message(username), channel)

        elif command.startswith("blessing"):
            self.send_msg(self.calculate_blessing(username), channel)

    def handle_message(self, user_message, username, channel):
        # every message gives faith, but few affect virtue
        harsh_penalty = ["anime", "senko"]
        penalty = ["cringe", "dab", "ff14", "ffxiv", "meow", "kuso", "git gud"]
        penalty_token = ["fun"] # need to be a whole token
        bonus = ["pog", "japanimation", "ez", "nice"]
        large_bonus = ["kami", "pray"]

        virtue_modifier = 0
        faith_modifier = 0
        penaltyGiven = False
        bonusGiven = False

        user_message = user_message.lower()

        for token in user_message.split(" "):
            if token in penalty_token:
                virtue_modifier -= 1
                penaltyGiven = True
        
        for term in harsh_penalty:
            if term in user_message:
                virtue_modifier -= 2
                faith_modifier -= 5
                penaltyGiven = True

        for term in penalty:
            if term in user_message:
                virtue_modifier -= 1
                penaltyGiven = True

        for term in bonus:
            if term in user_message:
                virtue_modifier += 1
                bonusGiven = True

        for term in large_bonus:
            if term in user_message:
                virtue_modifier += 2
                faith_modifier += 5

        if not bonusGiven and not penaltyGiven:
            # nothing special about the message
            faith_modifier += 1
        
        if virtue_modifier != 0:
            self.change_virtue(username, virtue_modifier)
        if faith_modifier != 0:
            self.update_faith(faith_modifier)