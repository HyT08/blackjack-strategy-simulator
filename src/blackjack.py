import numpy as np
import random

class Blackjack:
    def __init__(self, deck_type:str = 'finite', num_of_decks:int = 6, bankroll = 10000):
        self.bankroll = bankroll
        self.deck_type = deck_type
        self.deck = self._generate_deck(num_of_decks) if self.deck_type == 'finite' else None
        self._dealer_cards = []
        self.player_cards = []
    
    def _generate_deck(self, qty:int = 6):
        _possible_vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        deck = []
        for n in _possible_vals:
            frequency = 16 * qty if n == 10 else 4 * qty
            for x in range(frequency):
                    deck.append(n)
        return deck

    def bet(self, amount):
        self.bankroll -= amount if amount <= self.bankroll else 0
        return amount
    
    def _pull_card(self):
        if self.deck_type == 'finite':
            return self.deck.pop(random.randrange(0, len(self.deck)))
        else:
            return random.randrange(2, 12)
    
    def _calculate_value(cards = []):
        sum = sum(cards)
        return sum - 10 if 11 in cards and sum > 21 else sum

    