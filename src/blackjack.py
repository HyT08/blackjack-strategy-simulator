import random
import numpy as np

class Simulation:
    def __init__(self, performance_mode:bool=False, finite_deck:bool=True, 
                 num_of_decks:int=6, penetration:float=0.7 , 
                 bets_active:bool=True, bankroll:float=10000, 
                 dealer_hit_17:bool=True, blackjack_payout:float=1.5):
        
        self._performance_mode = performance_mode #performance mode for allowing higher number of simulations
        self._finite_deck = finite_deck
        self._deck_qty = num_of_decks
        self.penetration = penetration
        self._dealer_hit_17 = dealer_hit_17
        self._blackjack_payout = blackjack_payout
        self._bets_active = bets_active

        self.deck = self._generate_deck() if self._finite_deck else None
        if self._finite_deck:
            self._shuffle_deck()
            self._initial_deck_size = len(self.deck)
        else:
            self._initial_deck_size = 0

        self.initial_bankroll = bankroll
        self.bankroll = bankroll
        self.total_profit = 0
        self.games = 0

        self.current_bet = 0
        self.is_running = False
        self.doubled = False

        self.player_hand_val = 0
        self._dealer_hand_val = 0

        self.player_aces = 0
        self._dealer_aces = 0

        self._dealer_upcard = 0
        self._dealer_holecard = 0
        self._dealer_revealed = False

        if not self._performance_mode:
            self.player_hand = []
            self._dealer_hand = []
        self.player_card_count = 0
        self.player_wins = 0
        self.player_losses = 0
        self.pushes = 0

        self.player_blackjacks = 0
        self.dealer_blackjacks = 0

        self.player_results = []


    def _generate_deck(self):
        _possible_vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        deck = []
        for n in _possible_vals:
            frequency = 16 * self._deck_qty if n == 10 else 4 * self._deck_qty
            for i in range(frequency):
                deck.append(n)
        return deck
    
    def _shuffle_deck(self):
        return random.shuffle(self.deck)

    #function to allow a strategy to bet
    def bet(self, amount):
        if not self.is_running:
            self.current_bet = min(amount, self.bankroll)
            self.bankroll -= self.current_bet
        return self.current_bet
    
    def hit(self):
        if self.is_running: return 1
    
    def stand(self):
        if self.is_running: return 0

    def double(self):
        if self.is_running and self.player_card_count == 2: return 2
    
    def _pull_card(self):
        if self._finite_deck: return self.deck.pop()
        else: return random.choices([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], weights=(4, 4, 4, 4, 4, 4, 4, 4, 16, 4), k=1)[0]
    
    def get_player_hand(self):
        return self.player_hand if not self._performance_mode else None
    
    def get_player_hand_val(self):
        return self.player_hand_val
    
    def _get_dealer_hand_val(self):
        return self._dealer_hand_val
    
    def get_dealer_hand(self, full_hand=False):
        if full_hand or self._dealer_revealed:
            return (self._dealer_holecard, self._dealer_upcard)
        return self._dealer_upcard
    
    def get_bankroll(self):
        return self.bankroll

    #runs a single round of Blackjack
    def run(self, strategy:callable=None, visualize:bool=False):
        if self._finite_deck:
            if len(self.deck) < int(self._initial_deck_size * self.penetration):
                self.deck = self._generate_deck()
                self._shuffle_deck()
        if self._performance_mode: visualize = False
        if not self._performance_mode:
            self.player_hand = []
            self._dealer_hand = []
        self._dealer_aces = 0
        self.player_aces = 0
        self.player_card_count = 0
        self.is_running = False
        self.doubled = False
        self._dealer_revealed = False
        self.player_hand_val = 0
        self._dealer_hand_val = 0
        self._dealer_upcard = 0
        self._dealer_holecard = 0

        #Bet Logic
        if callable(strategy):
            strategy(self)
        if (self._bets_active and self.current_bet > 0) or not self._bets_active:
            if visualize: print(f'Bankroll: {self.bankroll}')
            if strategy is None or not callable(strategy):
                self.current_bet = min(int(input("Enter Bet: ")), self.bankroll)
                self.bankroll -= self.current_bet
            if visualize: print(f'Bet: {self.current_bet}')

            self.is_running = True
            self.games += 1

            #handing 2 cards to the player
            for i in range(2):
                card = self._pull_card()
                if not self._performance_mode: self.player_hand.append(card)
                self.player_hand_val += card
                self.player_card_count += 1
                if card == 11: self.player_aces += 1
                if self.player_hand_val > 21 and self.player_aces > 0:
                    self.player_hand_val -= 10
                    self.player_aces -= 1
            if visualize: print(f"Player: {self.player_hand} = {self.player_hand_val}")
                
            #handing 2 cards to the dealer:
            #hole card:
            card = self._pull_card()
            self._dealer_holecard = card
            self._dealer_hand_val += card
            if card == 11: self._dealer_aces += 1

            #upcard:
            card = self._pull_card()
            self._dealer_upcard = card
            self._dealer_hand_val += card
            if card == 11: self._dealer_aces += 1
            if visualize: print(f"Dealer: [/, {self._dealer_upcard}]")

            if self.player_hand_val == 21 and self._dealer_hand_val == 21:
                if self._performance_mode: self.pushes += 1
                else: self.player_results.append(0)
                self._dealer_revealed = True
                self.player_blackjacks += 1
                self.dealer_blackjacks += 1
                self.is_running = False
                self.bankroll += self.current_bet
                if visualize:
                    print('--Player + Dealer Blackjack!--')
                    print('-----Push-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                    print(f"EV: {self.get_player_ev()}")
                return 0
                
            #checking if player has a blackjack
            elif self.player_hand_val == 21:
                if self._performance_mode: self.player_wins += 1
                else: self.player_results.append(self._blackjack_payout)
                self.player_blackjacks += 1
                self.is_running = False
                self.bankroll += self.current_bet + self.current_bet * self._blackjack_payout
                self.total_profit += self.current_bet * self._blackjack_payout
                if visualize:
                    print('--Player Blackjack!--')
                    print('-----Win-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                    print(f"EV: {self.get_player_ev()}")
                return self._blackjack_payout
                
            #checking if dealer has a blackjack
            elif self._dealer_hand_val == 21:
                if self._performance_mode: self.player_losses += 1 
                else: self.player_results.append(-1)
                self.dealer_blackjacks += 1
                self.is_running = False
                self.total_profit -= self.current_bet
                if visualize:
                    print('--Dealer Blackjack!--')
                    print('-----Lose-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                    print(f"EV: {self.get_player_ev()}")
                return -1

            #getting player choice
            while self.player_hand_val <= 21:
                decision =  int(input("Hit(1) or Stand(0): ")) if strategy is None or not callable(strategy) else strategy(self)
                
                if decision not in (0, 1, 2):
                    raise ValueError(f"Invalid strategy decision: {decision}. Expected 0, 1 or 2.")
                
                #Hit
                elif decision == 1:
                    card = self._pull_card()
                    if not self._performance_mode: self.player_hand.append(card)
                    self.player_hand_val += card
                    self.player_card_count += 1
                    if card == 11: self.player_aces += 1
                    if self.player_hand_val > 21 and self.player_aces > 0:
                        self.player_hand_val -= 10
                        self.player_aces -= 1
                    if visualize:
                        print('-Hit-')
                        print(f"Player: {self.player_hand} = {self.player_hand_val}")
                
                #Double
                elif decision == 2:
                    if (self.current_bet * 2) <= self.bankroll:
                        self.bankroll -= self.current_bet
                        self.current_bet *= 2
                        self.doubled = True
                        card = self._pull_card()
                        if not self._performance_mode: self.player_hand.append(card)
                        self.player_hand_val += card
                        self.player_card_count += 1
                        if card == 11: self.player_aces += 1
                        if self.player_hand_val > 21 and self.player_aces > 0:
                            self.player_hand_val -= 10
                            self.player_aces -= 1
                        if visualize:
                            print('-Double-')
                            print(f"Player: {self.player_hand} = {self.player_hand_val}")
                        break
                    continue

                #Stand
                elif decision == 0:
                    if visualize: print('-Stand-')
                    break
                        
            #checking if player got busted
            if self.player_hand_val > 21:
                if self._performance_mode: self.player_losses += 1
                else: self.player_results.append(-2) if self.doubled else self.player_results.append(-1)
                self._dealer_revealed = True
                self.is_running = False
                self.total_profit -= self.current_bet
                if visualize:
                    print(f"Dealer: ({self._dealer_holecard}, {self._dealer_upcard}) = {self._dealer_hand_val}")
                    print('--Player Bust--')
                    print('-----Lose-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                    print(f"EV: {self.get_player_ev()}")
                return -1
                
            #dealer logic with soft 17
            else:
                self._dealer_revealed = True
                while self._dealer_hand_val < 17 or (self._dealer_hand_val == 17 and self._dealer_aces > 0 and self._dealer_hit_17):
                    card = self._pull_card()
                    if not self._performance_mode: self._dealer_hand.append(card)
                    self._dealer_hand_val += card
                    if card == 11: self._dealer_aces += 1
                    if self._dealer_hand_val > 21 and self._dealer_aces > 0:
                        self._dealer_hand_val -= 10
                        self._dealer_aces -= 1
                    if visualize: print(f"Dealer: ({self._dealer_holecard}, {self._dealer_upcard}) = {self._dealer_hand_val}")

            #checking if dealer got busted
            if self._dealer_hand_val > 21:
                if self._performance_mode: self.player_wins += 1
                else: self.player_results.append(2) if self.doubled else self.player_results.append(1)
                self.is_running = False
                self.bankroll += self.current_bet * 2
                self.total_profit += self.current_bet
                if visualize:
                    print('--Dealer Bust--')
                    print('-----Win-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                    print(f"EV: {self.get_player_ev()}")
                return 1
                
            #checking if player beat dealer
            elif self.player_hand_val > self._dealer_hand_val:
                if self._performance_mode: self.player_wins += 1
                else: self.player_results.append(2) if self.doubled else self.player_results.append(1)
                self.is_running = False
                self.bankroll += self.current_bet * 2
                self.total_profit += self.current_bet
                if visualize:
                    print('-----Win-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                    print(f"EV: {self.get_player_ev()}")
                return 1
                
            #checking if dealer beat player
            elif self.player_hand_val < self._dealer_hand_val:
                if self._performance_mode: self.player_losses += 1
                else: self.player_results.append(-2) if self.doubled else self.player_results.append(-1)
                self.is_running = False
                self.total_profit -= self.current_bet
                if visualize:
                    print('-----Lose-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                    print(f"EV: {self.get_player_ev()}")
                return -1
                
            #checking for push
            else:
                if self._performance_mode: self.pushes += 1
                else: self.player_results.append(0)
                self.is_running = False
                self.bankroll += self.current_bet
                if visualize:
                    print('-----Push-----')
                    if self._bets_active: print(f'Bankroll: {self.bankroll}')
                    print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                    print(f"EV: {self.get_player_ev()}")
                return 0
                

    def get_win_prob(self, wins):
        return (wins / self.games) if self.games > 0 else 0
    
    def get_loss_prob(self, losses):
        return (losses / self.games) if self.games > 0 else 0
    
    def get_push_prob(self, pushes):
        return (pushes / self.games) if self.games > 0 else 0
    
    def get_blackjack_prob(self, blackjacks):
        return (blackjacks / self.games) if self.games > 0 else 0
    
    def get_player_ev(self):
        if self._performance_mode:
            return self.total_profit / self.games if self.games > 0 else 0 #if performance mode is active only a single EV value is returned
        return np.mean(self.player_results) if len(self.player_results) > 0 else 0