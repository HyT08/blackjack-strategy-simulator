import random

class Simulation:
    def __init__(self, finite_deck:bool=True, num_of_decks:int=6, penetration:float=0.7 , bets_active:bool=False, bankroll:float=10000.00):
        self._finite_deck = finite_deck
        self.deck = self._generate_deck(num_of_decks) if self._finite_deck else None
        self._initial_deck_size = len(self.deck)
        self.penetration = penetration
        
        self.bankroll = bankroll
        self._bets_active = bets_active
        self.is_running = False
        self.current_bet = 0
        
        self._dealer_hand = []
        self.player_hand = []
        self.games = 0
        
        #track player performance:
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self.blackjacks = 0


    def _generate_deck(self, qty:int = 6):
        _possible_vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        deck = []
        for n in _possible_vals:
            frequency = 16 * qty if n == 10 else 4 * qty
            for i in range(frequency):
                    deck.append(n)
        return deck

    #function to allow a strategy to bet
    def bet(self, amount):
        if not self.is_running:
            self.current_bet = min(amount, self.bankroll)
            self.bankroll -= self.current_bet
        return self.current_bet
    
    def _pull_card(self):
        if self._finite_deck: return self.deck.pop(random.randrange(0, len(self.deck)))
        else: return random.choices([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], weights=(4, 4, 4, 4, 4, 4, 4, 4, 16, 4), k=1)[0]
    
    def calculate_value(self, hand):
        value = sum(hand)
        for i in range(hand.count(11)):
            if value > 21:
                value -= 10
        return value
    
    def get_player_hand(self):
        return self.player_hand
    
    def get_dealer_hand(self, full_hand:bool=False):
        return self._dealer_hand if full_hand or len(self.player_hand) > 2 else self._dealer_hand[1]
    
    def _check_bust(self, hand):
        return self.calculate_value(hand) > 21

    #runs a single round
    def run(self, strategy:callable = None, visualize:bool = True):
        self.deck = self._generate_deck() if len(self.deck) < int(self._initial_deck_size * self.penetration) else self.deck
        self._dealer_hand.clear()
        self.player_hand.clear()
        self.is_running = True
        self.games += 1

        #Bet Logic
        if (self._bets_active and self.current_bet > 0) or not self._bets_active:
                if self._bets_active:
                    if visualize: print(f'Bankroll: {self.bankroll}')
                    if strategy is None or not callable(strategy):
                        self.current_bet = min(int(input("Enter Bet: ")), self.bankroll)
                        self.bankroll = self.bankroll - self.current_bet
                    if visualize: print(f'Bet: {self.current_bet}')

                #handing 2 cards to the player
                for i in range(2):
                    self.player_hand.append(self._pull_card())
                if visualize: print(f"Player: {self.player_hand} = {self.calculate_value(self.player_hand)}")
                
                #handing 2 cards to the dealer
                for i in range(2):
                    self._dealer_hand.append(self._pull_card())
                if visualize: print(f"Dealer: [/, {self._dealer_hand[1]}]")

                #checking if player has a blackjack
                if self.calculate_value(self.player_hand) == 21:
                    self.blackjacks += 1
                    self.wins += 1
                    self.is_running = False
                    if visualize:
                        print('--Player Blackjack!--')
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return 1.5
                
                #checking if dealer has a blackjack
                elif self.calculate_value(self._dealer_hand) == 21:
                    self.losses += 1
                    self.is_running = False
                    if visualize:
                        print('--Dealer Blackjack!--')
                        print('-----Lose-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return -1

                #getting player choice
                while not self._check_bust(self.player_hand):
                    decision =  int(input("Hit(1) or Stand(0): ")) if strategy is None or not callable(strategy) else strategy()
                    
                    #Hit
                    if decision == 1:
                        self.player_hand.append(self._pull_card())
                        if visualize:
                            print('-Hit-')
                            print(f"Player: {self.player_hand} = {self.calculate_value(self.player_hand)}")

                    #Stand
                    elif decision == 0:
                        if visualize: print('-Stand-')
                        break
                    
                    #Double
                    elif decision == 2:
                        if (self.current_bet * 2) <= self.bankroll:
                            self.player_hand.append(self._pull_card())
                            self.current_bet *= 2
                            if visualize:
                                print('-Double-')
                                print(f"Player: {self.player_hand} = {self.calculate_value(self.player_hand)}")
                            break
                            
                #checking if player got busted
                if self._check_bust(self.player_hand):
                    self.losses += 1
                    self.is_running = False
                    if visualize:
                        print(f"Dealer: {self._dealer_hand} = {self.calculate_value(self._dealer_hand)}")
                        print('--Player Bust--')
                        print('-----Lose-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return -1
                
                #dealer logic with soft 17
                else:
                    while self.calculate_value(self._dealer_hand) < 17:
                            self._dealer_hand.append(self._pull_card())
                            if visualize: print(f"Dealer: {self._dealer_hand} = {self.calculate_value(self._dealer_hand)}")
                
                #checking if dealer got busted
                if self._check_bust(self._dealer_hand):
                    self.wins += 1
                    self.is_running = False
                    if visualize:
                        print('--Dealer Bust--')
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return 1
                
                #checking if player beat dealer
                elif self.calculate_value(self.player_hand) > self.calculate_value(self._dealer_hand):
                    self.wins += 1
                    self.is_running = False
                    if visualize:
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return 1
                
                else:
                    self.pushes += 1
                    self.is_running = False
                    if visualize:
                        print('-----Push-----')
                        print(f"Winrate: {self.get_win_prob() * 100}%")
                        print(f"EV: {self.get_ev()}")
                    return 0
               
    def get_win_prob(self):
        return (self.wins / self.games) if self.games > 0 else 0.0
    
    def get_loss_prob(self):
        return (self.losses / self.games) if self.games > 0 else 0.0
    
    def get_push_prob(self):
        return (self.pushes / self.games) if self.games > 0 else 0.0
    
    def get_blackjack_prob(self):
        return (self.blackjacks / self.games) if self.games > 0 else 0.0
    
    def get_ev(self):
        return (self.get_blackjack_prob() * 1.5) + (self.get_win_prob() * 1) + (self.get_push_prob() * 0) + (self.get_loss_prob() * -1)