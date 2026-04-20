import random

class Blackjack:
    def __init__(self, finite_deck:bool=True, num_of_decks:int=6, penetration:float=0.7 , bets_active:bool=False, bankroll:float=10000.00):
        self.bankroll = bankroll
        self._finite_deck = finite_deck
        self.deck = self._generate_deck(num_of_decks) if self._finite_deck else None
        self._initial_deck_size = len(self.deck)
        self.penetration = penetration
        self._bets_active = bets_active
        self.current_bet = 0
        self._dealer_hand = []
        self.player_hand = []
        self.games = 0
        #for the player:
        self.wins = 0
        self.losses = self.games - self.wins
        self.pushes = self.games - self.losses
        self.blackjacks = 0
        self.win_prob = (self.wins / self.games) * 100 if self.games > 0 else 0.0
        self.loss_prob = 100.00 - self.win_prob
        self.push_prob = 100.00 - self.loss_prob
        self.blackjack_prob = self.blackjacks / self.games
        self.expected_value = (self.blackjack_prob * 1.5) (self.win_prob * 1) + (self.push_prob * 0) + (self.loss_prob * -1)
    
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
        return self.current_bet
    
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
    
    def get_player_hand(self):
        return self._calculate_value(self.player_hand)
    
    def get_dealer_hand(self, full_hand:bool=False):
        return self._dealer_hand if full_hand or len(self._dealer_hand) > 2 else self._dealer_hand[1]
    
    def _check_bust(self, hand):
        return self._calculate_value(hand) > 21

    #runs a single round
    def run(self, strategy:callable = None):
        self.deck = self._generate_deck() if len(self.deck) < int(self._initial_deck_size * self.penetration) else self.deck
        self._dealer_hand.clear()
        self.player_hand.clear()
        self.games += 1

        if (self._bets_active and self.current_bet > 0) or not self._bets_active:
                if self._bets_active:
                    print(f'Bankroll: {self.bankroll}')
                    self.current_bet = min(int(input("Enter Bet: ")), self.bankroll) if strategy is None or not callable(strategy) else self.current_bet
                    self.bankroll = self.bankroll - self.current_bet  if strategy is None or not callable(strategy) else self.bankroll
                    print(f'Bet: {self.current_bet}')

                for i in range(2):
                    self.player_hand.append(self._pull_card())
                if self._calculate_value(self.player_hand) == 21:
                    self.blackjacks += 1
                    self.wins += 1
                    return 1.5
                print(f'Player: {self.player_hand}')
                print(self._calculate_value(self.player_hand))
            
                for i in range(2):
                    self._dealer_hand.append(self._pull_card())
                print(f'Dealer: /, {self._dealer_hand[1]}')

                while not self._check_bust(self.player_hand):
                    decision =  int(input("Hit(1) or Stand(0): ")) if strategy is None or not callable(strategy) else strategy()
                    if decision == 1: #Hit
                        self.player_hand.append(self._pull_card())
                        print(f'Player: {self.player_hand}')
                        print(self._calculate_value(self.player_hand))

                    elif decision == 0: #Stand
                        break
                
                if self._check_bust(self.player_hand):
                    return -1
                
                else:
                    while self._calculate_value(self._dealer_hand) < 17:
                            self._dealer_hand.append(self._pull_card())
                            print(self._calculate_value(self._dealer_hand))
                
                if self._check_bust(self._dealer_hand) or self._calculate_value(self.player_hand) > self._calculate_value(self._dealer_hand):
                    self.wins += 1
                    return 1
                else:
                    self.pushes +=1
                    return 0
               
    def get_winrate(self):
        return self.win_prob
    
    def get_ev(self):
        return self.expected_value