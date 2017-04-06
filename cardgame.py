#! /usr/bin/python
# coding=utf-8

import random

SUITS = (('♥︎','Hearts'), ('♦︎','Diamonds'), ('♠︎','Spades'), ('♣︎','Clubs'))
#SUITS = (('h','Hearts'), ('d','Diamonds'), ('s','Spades'), ('c','Clubs'))
FACEVALS = (('A', 'Ace'), (2, 'Two'), (3, 'Three'), (4, 'Four'), (5, 'Five'), 
            (6, 'Six'), (7, 'Seven'), (8, 'Eight'), (9, 'Nine'), (10, 'Ten'), 
            ('J', 'Jack'), ('Q', 'Queen'), ('K', 'King'))


class GameError(Exception):
    pass


class Card(object):
    """
    A playing card with suit, face value and a visibility flag for if the card
    can be seen by the entire table
    """
    def __init__(self, suit, val, visible=False):
        self.suit = suit
        self.val = val
        self.visible = visible
    
    def shortStr(self):
        return "{}{}".format(self.val[0], self.suit[0])
        
    def longStr(self):
        return "{} of {}".format(self.val[1], self.suit[1])


class Deck(object):
    """ Provides a deck of cards and discard pile for a card game """
    def __init__(self, cards):
        self._cards = list(cards)
    
    def shuffleCards(self):
        """ randomizes card order """
        random.shuffle(self._cards)
    
    def addCard(self, card):
        self._cards.append(card)
        
    def isEmpty(self):
        if self._cards:
            return False
        return True
    
    def dealCard(self):
        """ deals a card from the top of the deck """
        if not self._cards:
            raise GameError("Cannot deal from empty deck.")
        return self._cards.pop()


class Currency(object):
    def __init__(self, kind, plural=None):
        self.kind = kind
        if not plural:
            self.plural = str(kind) + 's'
        else:
            self.plural = plural


class Bet(object):
    def __init__(self, currency, amount, kind='standard'):
        self.currency = currency
        self.amount = amount
        # provided for tracking special bets like "Double or Nothing"
        self.kind = kind
        
    def getPrintable(self):
        if self.amount == 1:
            return "{} bet of {} {}".format(self.kind, self.amount, self.currency.kind)
        else:
            return "{} bet of {} {}".format(self.kind, self.amount, self.currency.plural)


class Player(object):
    def __init__(self, name):
        self._cards = list()
        self._name = name
        self._bank = dict()
    
    def showCards(self, omnipotent=False):
        if omnipotent:
            return ", ".join([card.shortStr() for card in self._cards])
        else:
            return ", ".join([card.shortStr() if card.visible else '🂠' for card in self._cards])
    
    def who(self):
        return self._name
    
    def drawCard(self, card):
        self._cards.append(card)
    
    def playCard(self, card):
        try:
            c = self._cards.pop(self._cards.index(card))
        except ValueError:
            raise GameError("Card is not in hand")
        else:
            return c
    
    def discardHand(self):
        discards = self._cards
        self._cards = list()
        return discards
        
    def addFunds(self, currency, amount):
        if currency in self._bank:
            self._bank[currency] += amount
        else:
            self._bank[currency] = amount
    
    def removeFunds(self, currency, amount):
        if currency in self._bank:
            if self._bank[currency] >= amount:
                self._bank[currency] -= amount
                return amount
            else:
                raise GameError("Insufficient funds")
        else:
            raise GameError("Requested currency not in bankroll")
    
    def getFunds(self, currency):
        if not self._bank:
            return None
        if currency in self._bank:
            return self._bank[currency]
        else:
            return 0
    
    def fundsStr(self, currency):
        try:
            if self._bank[currency] == 1:
                return "{} {}".format(self._bank[currency], currency.kind)
            else:
                return "{} {}".format(self._bank[currency], currency.plural)
        except KeyError:
            pass
    
    def makeBet(self, currency, amount, kind):
        if amount < 0:
            raise GameError("You can't make a negative bet.")
        funds = self.removeFunds(currency, amount)
        return Bet(currency, funds, kind)


class Game(object):
    def __init__(self, players, deck):
        # list of player objects
        self._players = players
        # deck object
        self._deck = deck
        # discard pile object
        self._discards = []
        # dict of bets keyed to players
        self._pot = {}
        # player instance
        self._activePlayer = None
    
    def returnDiscarded(self):
        """ Returns discarded cards to the deck """
        while self._discards:
            card = self._discards.pop()
            card.visible = False
            self._deck.addCard(card)
    
    def discardCards(self, cards):
        """ Places card(s) in the discard pile """
        for card in cards:
            card.visible = True
            self._discards.append(card)
    
    def showDiscards(self):
        return ", ".join([card.shortStr() for card in self._discards])
    
    def addPlayer(self, player):
        self._players.insert(0, player)
    
    def removePlayer(self, player):
        try:
            p = self._players.pop(self._players.index(player))
        except ValueError:
            raise GameError("Player is not at table")
        else:
            return p
    
    def nextPlayer(self):
        playerindx = self._players.index(self._activePlayer) + 1
        try:
            self._activePlayer = self._players[playerindx]
        except IndexError:
            self._activePlayer = None
    
    def pullCardFromDeck(self):
        if self._deck.isEmpty():
#            print("no more cards in the deck time to shuffle...")
            if self._discards:
                self.returnDiscarded()
                self._deck.shuffleCards()
            else:
                raise GameError("Table out of cards")
        return self._deck.dealCard()
    
    def dealCardToPlayer(self, player, show=False):
        card = self.pullCardFromDeck()
        if show:
            card.visible = True
        player.drawCard(card)
    
    def getBets(self):
        return self._pot
    
    def addBet(self, bet, player):
        self._pot[player].append(bet)
        
    def clearBets(self):
        self._pot = dict()
        
    def updatePlayerBet(self, player, newbet):
        try:
            self._pot[player] = newbet
        except KeyError:
            raise("No existing bets to update")