#! /usr/bin/python
# coding=utf-8
# blackjack.py

import cardgame
import time


class BlackjackCard(cardgame.Card):
    def getVal(self):
        if self.val[0] == 'A':
            return 1
        elif self.val[0] in range(2, 11):
            return self.val[0]
        elif self.val[0] in ('J', 'Q', 'K'):
            return 10


class BlackjackPlayer(cardgame.Player):
    def getBestHand(self):
        handVal = sum([i.getVal() for i in self._cards])
        
        if ( handVal <= 11 ) and self.hasAce():
            return handVal + 10
        else:
            return handVal
        
    def hasAce(self):
        for i in self._cards:
            if i.val[0] == 'A':
                return True
        return False
        
    def hasNatural(self):
        if (self.getBestHand() == 21) and (len(self._cards) == 2):
            return True
        return False
    
    def busted(self):
        if self.getBestHand() > 21:
            return True
        else:
            return False
    
    def getStandardBet(self, currency):
        betval = raw_input("You have {}. How much would you like to bet?: "\
            .format(self.fundsStr(currency)))
        try:
            betval = int(betval)
        except:
            return self.getStandardBet(currency)
            
        if betval == 0:
            return None
        
        try:
            bet = self.makeBet(currency, betval, 'standard')
        except cardgame.GameError as e:
            print "Bet invalid: {}".format(e.message)
            return self.getStandardBet(currency)
        else:
            return bet
    
    def takeHit(self):
        answer = makeChoice("Will you hit or stay?", ["hit","stay"])
        if answer == "hit":
            return True
        else:
            return False


class BlackjackDealer(BlackjackPlayer):
    def getStandardBet(self, currency):
        return None
    
    def takeHit(self):
        time.sleep(.5)
        if self.getBestHand() < 17:
            print("Dealer took a hit.")
            return True
        else:
            print("Dealer stays.")
            return False
    
    def payout(self, currency, amount):
        # if dealer has a bankroll then funds come from there. this can raise
        # an error if the dealer overdraws funds
        # otherwise funds are 
        if self._bank:
            pay = self.removeFunds(currency, amount)
            return (currency, pay)
        else:
            return (currency, amount)
    
    def addFunds(self, currency, amount):
        if self._bank:
            super(BlackjackPlayer, self).addFunds(currency, amount)


class BlackjackGame(cardgame.Game):
    DOLARS = cardgame.Currency('dolar', 'dolars')
    CIGARETTES = cardgame.Currency('cig', 'cigs')
    CLOTHES = cardgame.Currency('piece of clothing', 'pieces of clothing')
    CHIPS = cardgame.Currency('chip', 'chips')
    STAKES = {"dolars": (DOLARS, 100),
              "cigarettes": (CIGARETTES, 20),
              "chips": (CHIPS, 50),
              "clothing": (CLOTHES, 10)}

    def __init__(self):
        deck = cardgame.Deck(STANDARDDECK)
        deck.shuffleCards()
        self._dealer = self.makeDealer()
        self._stakes = self.STAKES[makeChoice("What are you betting with?", 
            self.STAKES.keys())]
        super(BlackjackGame, self).__init__([self._dealer], deck)
    
    def makeDealer(self):
        dealer = BlackjackDealer(name="Dealer")
        dealer._bank = None
        return dealer
    
    def makePlayer(self):
        name = raw_input("What's your name?: ")
        player = BlackjackPlayer(name=name)
        player.addFunds(currency=self._stakes[0], amount=self._stakes[1])
        print("You have a starting bankroll of {}".format(
            player.fundsStr(self._stakes[0])))
        return player
    
    def dealToEveryone(self):
        for player in self._players:
            # deal hole
            self.dealCardToPlayer(player)
            # all cards after hole will be visible
            self.dealCardToPlayer(player, show=True)
    
    def takeStartingBets(self):
        for player in self._players:
            bet = player.getStandardBet(self._stakes[0])
            self._pot[player] = bet
        
        for player in self._players:
            try:
                print("Player {} made a {}".format(player.who(), 
                    self._pot[player].getPrintable()))
            except:
                print("Player {} made no bets.".format(player.who()))
    
    def showHands(self):
        for player in self._players:
            if player == self._activePlayer:
                print("Your hand: {}".format(player.showCards(omnipotent=True)))
            else:
                print("{}'s hand: {}".format(player.who(), player.showCards()))
    
    def dealOptions(self):
        for player in self._players:
            # skip players that did not bet
            if player not in self._pot:
                continue
            print "{}'s turn. Hand: {}".format(
                    player.who(), player.showCards(omnipotent=True))
            # you can offer surrender here
            # self.payPlayer(player, 'surrender')
            while (not player.busted()) and player.takeHit():
                self.dealCardToPlayer(player, show=True)
                print "{}'s hand: {}".format(
                        player.who(), player.showCards(omnipotent=True))
                if player.busted():
                    print "{} busted!".format(player.who())
            time.sleep(.5)
    
    def calcWinners(self):
        if self._dealer.busted():
            dealer_best = 0
        else:
            dealer_best = self._dealer.getBestHand()
        for player in self._players:
            if player == self._dealer:
                continue
            elif player.busted():
                self.payPlayer(player, 'loss')
                continue
            if player.hasNatural():
                if self._dealer.hasNatural():
                    self.payPlayer(player, 'push')
                else:
                    self.payPlayer(player, 'natural')
            elif player.getBestHand() > dealer_best:
                self.payPlayer(player, 'win')
            elif player.getBestHand() == dealer_best:
                self.payPlayer(player, 'push')
            else:
                self.payPlayer(player, 'loss')
    
    def payPlayer(self, player, win_type):
        bet = self._pot[player]
        # no payout if no bet was made
        if not bet:
            return
        # winnings for a standard bet with no insurance/doubles/side bets/etc.
        if bet.kind == 'standard':
            if win_type == 'loss':
                print("You lost this round {}.".format(player.who()))
                self._dealer.addFunds(bet.currency, bet.amount)
                return
            elif win_type == 'push':
                print("No winners this round {}.".format(player.who()))
                player.addFunds(bet.currency, bet.amount)
            elif win_type == 'win':
                print("You won this round {}.".format(player.who()))
                player.addFunds(bet.currency, bet.amount)
                win_amt = bet.amount
                currency, amount = self._dealer.payout(bet.currency, win_amt)
                player.addFunds(currency, amount)
            elif win_type == 'natural':
                print("You won this round with a natural blackjack {}!"
                      .format(player.who()))
                player.addFunds(bet.currency, bet.amount)
                win_amt = int(round(bet.amount * 1.5))
                currency, amount = self._dealer.payout(bet.currency, win_amt)
                player.addFunds(currency, amount)
            elif win_type == 'surrender':
                win_amt == int(bet.amount * 0.5)
                self._dealer.addFunds(bet.currency, bet.amount)
                # remove the bet from the pot so the player is not paid later
                # if dealer busts
                self._pot[player] = None
    
    def resetRound(self):
        self.clearBets()
        for player in self._players:
            discards = player.discardHand()
            self.discardCards(discards)
    
    def checkPlayerExit(self, player, curency):
        if player.getFunds(curency) == 0:
            print("Player {} has run out of funds and was ejected from the"
                " casino!".format(player.who()))
            self.removePlayer(player)
        else:
            choice = makeChoice("Would you like to cash out {}?"\
                .format(player.who()), ("yes", "no"))
            if choice == "yes":
                print("You left the table with {}.".format(player.fundsStr(
                    curency)))
                self.removePlayer(player)

    def checkForEndGame(self):
        curency = self._stakes[0]
        # check that dealer is not broke
        # boot players with no funds
        for player in self._players:
            if player == self._dealer:
                if player.getFunds(curency) == 0:
                    print("The dealer has run out of {}. Game over.".format(
                        curency.plural))
                    exit(0)
            else:
                self.checkPlayerExit(player, curency)
        if len(self._players) <= 1:
            print("No more players at the table. Game Over.")
            exit(0)
    
    def round(self):
        self.takeStartingBets()
        self.dealToEveryone()
        self.showHands()
        time.sleep(.5)
        # dealer wins automatically if they have a natural 21(blackjack)
        # in this case no cards are dealt
        if self._dealer.hasNatural():
            print("Dealer has natural 21(blackjack): {}".format(
                self._dealer.showCards(omnipotent=True)))
        else:
            self.dealOptions()
        self.calcWinners()
        self.resetRound()
        self.checkForEndGame()
    
    def run(self):
        """
        Setup Game
        - get player(s) names
        - select what currency player(s) will be betting with
        - build players, dealer, hands, decks and table
        - start round
        """
        player = self.makePlayer()
        self.addPlayer(player)
        while makeChoice("Add another player?", ["yes","no"]) == "yes":
            player = self.makePlayer()
            self.addPlayer(player)
        print("Game has the following players: {}"\
              .format([player.who() for player in self._players]))
        while True:
            self.round()


STANDARDDECK = tuple(BlackjackCard(suit, val) 
                     for suit in cardgame.SUITS 
                     for val in cardgame.FACEVALS)
                     


def makeChoice(prompt, choices=None):
    chosen = raw_input("{} {}?: ".format(prompt.rstrip('?'), choices))
    lst = []
    for choice in choices:
        if choice.lower().startswith(chosen.lower()):
            lst.append(choice)
    if len(lst) == 1:
        return lst[0]
    return makeChoice(prompt, choices)
    

"""
Round
    - get player bets
    - deal to players until they stay or bust
    - deal to dealer until they stay or bust
    - determine winner(s)
    - payout to winner(s)
    - kick player from table if they are out of $
    - end game if there are no players
    - prompt to continue playing or cash out
    - start next round
"""


if __name__ == "__main__":
    try:
        game = BlackjackGame()
        game.run()
    except KeyboardInterrupt:
        print("\nUh Oh! Someone tipped off the fuzz.\nGame Over!")
        exit()