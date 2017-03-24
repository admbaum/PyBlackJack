#! /usr/bin/python
# coding=utf-8
# blackjack.py

import cardgame


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
        
        if ( handVal <= 11 ) and self.hasAce:
            return handVal + 10
        else:
            return handVal
        
    def hasAce(self):
        for i in self._cards:
            if i.val[0] == 'A':
                return True
        return False
    
    def busted(self):
        if self.getBestHand() > 21:
            return True
        else:
            return False
    
    def getStandardBet(self, currency):
        betval = raw_input("You have {}. How much would you like to bet?: "\
                           .format(self._bankroll.getPrintable(currency)))
        try:
            betval = int(betval)
        except:
            return self.getStandardBet(currency)

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
        if self.getBestHand() < 17:
            return True
        else:
            return False
            
    def payout(self, currency, amount):
        if self.bankroll:
            pass
        else:
            pass


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
        dealer = self.makeDealer()
        self._stakes = self.STAKES[makeChoice("What are you betting with?", 
                                         self.STAKES.keys())]
        super(BlackjackGame, self).__init__([dealer], deck)
    
    def makeDealer(self):
        name = "Dealer"
        return BlackjackDealer(bankroll=None, name=name)
    
    def makePlayer(self):
        name = raw_input("What's your name?: ")
        bank = cardgame.Bankroll(currency=self._stakes[0], amount=self._stakes[1])
        print "You have a starting bankroll of {}".format(bank.getPrintable(self._stakes[0]))
        return BlackjackPlayer(bankroll=bank, name=name)
    
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
                print "Player {} made a {}".format(player.who(), 
                        self._pot[player].getPrintable())
            except:
                print "Player {} made no bets.".format(player.who())
        
    def showHands(self):
        for player in self._players:
            if player == self._activePlayer:
                print "Your hand: {}".format(player.showCards(omnipotent=True))
            else:
                print "{}'s hand: {}".format(player.who(), player.showCards())
                
    def dealOptions(self):
        for player in self._players:
            print "{}'s turn. Your hand: {}".format(player.who(), player.showCards(omnipotent=True))
            while (not player.busted()) and player.takeHit():
                self.dealCardToPlayer(player, show=True)
                print "{}'s hand: {}".format(player.who(), player.showCards(omnipotent=True))
                if player.busted():
                    print "{} busted!".format(player.who())
    
    def calcWinners(self):
        for player in self._players:
            pass
    
    def round(self):
        self.takeStartingBets()
        self.dealToEveryone()
        self.showHands()
        self.dealOptions()
        # Todo
        # self.calcWinners()
        # payout to winners
        # clear board/hands
        # look at End Game scenarios
        # prompt for another round
    
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
        print "Game has the following players: {}".format([player.who() for player in self._players])
        
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
        print("Game Over!")
        exit()