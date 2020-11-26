import random
from utils import messaging
import re


class Roller:
    rolls = []
    goodMessages = messaging.goodDefault.copy()
    badMessages = messaging.badDefault.copy()
    frenzyMessages = messaging.frenzyDefault.copy()
    jackMessages = messaging.jackDefault.copy()
    natalieMessages = messaging.natalieDefault.copy()
    teddieMessages = messaging.teddieDefault.copy()
    paradoxFail = messaging.badParadox.copy()

    def __init__(self, splat='default', flavour=True):
        """
        Class for holding details of a player and making their rolls.
        Args:
            ID (str): discord ID of player
            splat (str): which gameline the player has set
            flavour (bool): whether flavour messaging is active
        """

        self.rolls = []
        self.splat = splat
        self.changeSplat(splat)
        self.flavour = flavour

    @classmethod
    def from_dict(cls, character_dict):
        return cls(
            splat=character_dict['splat'],
            flavour=character_dict['flavour'],
        )

    def changeSplat(self, splat):
        """
        Set flavour messaging for selected splat
        Args:
            splat (str): which gameline the player has set

        Returns (str): Partial message confirming that splat was set

        """
        if splat == 'mage':
            self.splat = 'mage'
            self.goodMessages =  messaging.goodDefault.copy() + messaging.goodMage.copy()
            self.badMessages = messaging.badDefault.copy() + messaging.badMage.copy()

            return "Splat set to Mage in "

        elif splat == 'default':
            self.splat = 'default'
            self.goodMessages = messaging.goodDefault.copy()
            self.badMessages = messaging.badDefault.copy()

        elif splat:
            return "No custom settings for " + splat + ". Messaging unchanged in "

    def roll_set(self, dice, rote=False, again=10, paradox=False, frenzy=False, sender_nick=""):
        """
        Roll a set of dice
        Args:
            dice (int): amount of dice to roll
            rote (bool): whether this is a rote roll
            again (int): lowest number that is rerolled
            paradox (bool): whether this is a paradox roll

        Returns (list of str): roll messages to return
        """

        if dice < 1:
            return ['Select at least 1 die.']

        self.rolls = []
        successes = 0

        # fail collector in case it is a rote
        fails = []

        for die in range(0, dice):
            # roll each die
            result = self.roll_die(again, one_die=dice==1)
            if result == 0:
                # if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
            else:
                successes += result

        if rote:
            for die in fails:
                successes += self.roll_die(again, rote_reroll=True, one_die=dice==1)

        messages = []

        # add a summary message
        if successes < 0:
            successes = 0
        out = f"[userID] rolled {str(dice)} dice and got **{str(successes)} success"
        if successes != 1:
            out += "es**."
        else:
            out += "**."
        for message in self.rolls:
            # find dice value
            value = re.search(r'\d{1,2}', message).group(0)
            if "exploded" in message:
                out += "(" + value + ")"
            elif "rote" in message:
                out += " Rote:" + value
            else:
                out += " " + value

        messages.append(out)

        # check for positive or negative message
        if dice <= 1:
            if successes >= 1:
                messages.append(self.bot_message("good", sender_nick))
        elif dice > 1 and self.flavour and not paradox:
            if successes == 0:
                if frenzy:
                    messages.append(self.bot_message("frenzy", sender_nick))
                else:
                    messages.append(self.bot_message("bad", sender_nick))
            elif successes >= 5:
                messages.append(self.bot_message("good", sender_nick))
        elif self.flavour and paradox:
            if successes != 0:
                messages.append(self.bot_message("paradox", sender_nick))

        return messages

    def special_roll_set(self, dice, rote=False, again=11, paradox=False, frenzy=False, sender_nick=""):
        """
        Roll a set of dice
        Args:
            dice (int): amount of dice to roll
            rote (bool): whether this is a rote roll
            again (int): lowest number that is rerolled
            paradox (bool): whether this is a paradox roll

        Returns (list of str): roll messages to return
        """

        if dice < 1:
            return ['Select at least 1 die.']

        self.rolls = []
        successes = 0
        ones = 0

        # fail collector in case it is a rote
        fails = []

        for die in range(0, dice):
            # roll each die
            result = self.special_roll_die(again)
            if result <= 0:
                # if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
                if result == -1:
                    successes -= 1
                    ones += 1
            else:
                successes += result

        if rote:
            for die in fails:
                successes += self.special_roll_die(again, rote_reroll=True)

        messages = []

        # add a summary message
        if successes < 0:
            successes = 0
            ones_word = 'one'
            if ones > 1:
                ones_word += 's'
            out = f"[userID] rolled {str(dice)} dice, subtracted {str(ones)} {ones_word}, and got **{str(successes)} success"
        else:
            out = f"[userID] rolled {str(dice)} dice and got **{str(successes)} success"
        if successes != 1:
            out += "es**."
        else:
            out += "**."
        for message in self.rolls:
            # find dice value
            value = re.search(r'\d{1,2}', message).group(0)
            if "exploded" in message:
                out += "(" + value + ")"
            elif "rote" in message:
                out += " Rote:" + value
            else:
                out += " " + value

        messages.append(out)

        # check for positive or negative message
        if self.flavour and not paradox:
            if successes == 0:
                if frenzy:
                    messages.append(self.bot_message("frenzy", sender_nick))
                else:
                    messages.append(self.bot_message("bad", sender_nick))
            elif successes >= 5:
                messages.append(self.bot_message("good", sender_nick))
        elif self.flavour and paradox:
            if successes != 0:
                messages.append(self.bot_message("paradox", sender_nick))

        return messages

    def bot_message(self, messagetype, sender):
        """
        Sends a random positive/negative message with very good or very bad rolls
        Args:
            messagetype (str): type of messaging to add

        Returns (str): message to add
        """
        sender_specific_msgs = []
        sender_specific_good_msgs = []
        if "natalie" in sender:
            sender_specific_msgs.extend(self.natalieMessages)
            sender_specific_good_msgs.extend(messaging.natGood.copy())
        if "teddie" in sender:
            sender_specific_msgs.extend(self.eddieMessages)
            sender_specific_good_msgs.extend(messaging.tedGood.copy())
        if "jack" in sender:
            sender_specific_msgs.extend(self.jackMessages)
            sender_specific_good_msgs.extend(messaging.jackGood.copy())
        out = ''
        if messagetype == 'good':
            out = random.choice(self.goodMessages + sender_specific_good_msgs)
        elif messagetype == 'bad':
            out = random.choice(self.badMessages + sender_specific_msgs)
        elif messagetype == 'frenzy':
            out = random.choice(self.frenzyMessages + sender_specific_msgs)
        elif messagetype == 'paradox':
            out = random.choice(self.paradoxFail)

        return out

    def roll_die(self, again=10, explode_reroll=False, rote_reroll=False, one_die=False):
        """
        Rolls a single die, calculates number of successes and updates self.rolls
        Args:
            again (int): lowest number to reroll
            explode_reroll (bool): whether it is a reroll of an exploded dice
            rote_reroll (bool): whether it is a reroll of a rote

        Returns (int): number of successes

        """

        value = random.randrange(1, 11)

        if explode_reroll and rote_reroll:
            self.rolls.append("[userID] rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.rolls.append("[userID] rolled exploded die: " + str(value))
        elif rote_reroll:
            self.rolls.append("[userID] rolled rote die: " + str(value))
        else:
            self.rolls.append("[userID] rolled " + str(value))

        # Checks for success/explosions
        if value >= again:
            # Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif one_die:
            if value == 10:
                return 1
            else:
                return 0
        elif value >= 8:
            return 1
        else:
            return 0

    def special_roll_die(self, again=10, explode_reroll=False, rote_reroll=False):
        """
        Rolls a single die, calculates number of successes and updates self.rolls
        Args:
            again (int): lowest number to reroll
            explode_reroll (bool): whether it is a reroll of an exploded dice
            rote_reroll (bool): whether it is a reroll of a rote

        Returns (int): number of successes

        """

        value = random.randrange(1, 11)

        if explode_reroll and rote_reroll:
            self.rolls.append("[userID] rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.rolls.append("[userID] rolled exploded die: " + str(value))
        elif rote_reroll:
            self.rolls.append("[userID] rolled rote die: " + str(value))
        else:
            self.rolls.append("[userID] rolled " + str(value))

        # Checks for success/explosions
        if value >= again:
            # Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            return 1
        elif value == 1:
            return -1
        else:
            return 0

    @staticmethod
    def roll_special():
        """
        Roll a single die
        Returns (str): Result of roll
        """
        value = random.randint(1, 10)
        return "[userID] rolled a " + str(value) + "!"

    def roll_chance(self, paradox=False):
        """
        Rolls a chance die
        Returns (list of str): Messages to send
        """
        value = random.randint(1, 10)
        messages = ["[userID] chance rolled " + str(value)]

        # Check if failure, botch or success
        if value == 10:
            messages.append("[userID] got a success!")
            if self.flavour:
                if paradox:
                    messages.append(self.bot_message("paradox"))
                else:
                    messages.append(self.bot_message("good"))
        elif value == 1:
            messages.append("[userID] botched!")
            if self.flavour:
                if paradox:
                    messages.append(self.bot_message("good"))
                else:
                    messages.append(self.bot_message("bad"))
        else:
            messages.append("[userID] failed!")
            if self.flavour and not paradox:
                messages.append(self.bot_message("bad"))

        return messages
