import numpy as np
import random

class Blackjack:
    def __init__(self, finite_deck:bool = True, num_of_decks:int = 6, bets_active:bool = False, bankroll = 10000):
        self.bankroll = bankroll
        self._finite_deck= finite_deck
        self.deck = self._generate_deck(num_of_decks) if self._finite_deck else None
        self._bets_active = bets_active
        self.current_bet = 0
        self._dealer_hand = []
        self.player_hand = []
    
    def _generate_deck(self, qty:int = 6):
        _possible_vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        deck = []
        for n in _possible_vals:
            frequency = 16 * qty if n == 10 else 4 * qty
            for i in range(frequency):
                    deck.append(n)
        return deck

    def bet(self, amount):
        self.current_bet = min(amount, self.bankroll)
        self.bankroll -= self.current_bet
        return amount
    
    def _pull_card(self):
        if self._finite_deck:
            return self.deck.pop(random.randrange(0, len(self.deck)))
        else:
            return random.choices([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], weights=(4, 4, 4, 4, 4, 4, 4, 4, 16, 4), k=1)[0]
    
    def _calculate_value(self, hand):
        value = sum(hand)

        for i in range(hand.count(11)):
            if value > 21:
                value -= 10
        
        return value
    
    def _check_bust(self, hand):
        return self._calculate_value(hand) > 21

    #runs a single round
    def run(self):
        self._dealer_hand.clear()
        self.player_hand.clear()
        decision = None

        if (self._bets_active and self.current_bet > 0) or not self._bets_active:
            print(f'Bankroll: {self.bankroll}')
            print(f'Bet: {self.current_bet}')

            for i in range(2):
                self.player_hand.append(self._pull_card())
            print(f'Player: {self.player_hand}')
            print(self._calculate_value(self.player_hand))
        
            for i in range(2):
                self._dealer_hand.append(self._pull_card())
            print(f'Dealer: /, {self._dealer_hand[1]}')

            while not self._check_bust(self.player_hand):
                if decision == 'Hit':
                    self.player_hand.append(self._pull_card())
                    print(self._calculate_value(self.player_hand))

                elif decision == 'Stand':
                    break
            
            if self._check_bust(self.player_hand):
                return -1
            
            else:
                while self._calculate_value(self._dealer_hand) < 17:
                        self._dealer_hand.append(self._pull_card())
                        print(self._calculate_value(self._dealer_hand))
            
            return 1 if self._check_bust(self._dealer_hand) or self._calculate_value(self.player_hand) > self._calculate_value(self._dealer_hand) else 0