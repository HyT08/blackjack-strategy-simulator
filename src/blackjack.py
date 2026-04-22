import random
import numpy as np

class Simulation:
    def __init__(self, performance_mode:bool=False, finite_deck:bool=True, num_of_decks:int=6, penetration:float=0.7 , bets_active:bool=False, bankroll:float=10000.00, dealer_hit_17:bool=False, blackjack_payout:float=1.5):
        self._performance_mode = performance_mode #performance mode for allowing higher number of simulations
        self._finite_deck = finite_deck
        self._deck_qty = num_of_decks
        self.deck = self._generate_deck() if self._finite_deck else None
        self._initial_deck_size = len(self.deck)
        self.penetration = penetration
        
        self.bankroll = bankroll
        self._bets_active = bets_active
        self.is_running = False
        self.current_bet = 0
        self._blackjack_payout = blackjack_payout
        self.total_profit = 0
        
        self._dealer_hand = []
        self.player_hand = []
        self._dealer_hit_17 = dealer_hit_17
        self.games = 0
        
        self.player_results = [] #list of results for more detailed analysis
        
        #counters for better performance:
        self.player_wins = 0
        self.player_losses = 0
        self.pushes = 0
        
        self.player_blackjacks = 0
        self.dealer_blackjacks = 0


    def _generate_deck(self):
        _possible_vals = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        deck = []
        for n in _possible_vals:
            frequency = 16 * self._deck_qty if n == 10 else 4 * self._deck_qty
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
        if full_hand or len(self._dealer_hand) > 2: return self._dealer_hand  
        elif len(self._dealer_hand) == 2: return self._dealer_hand[1]
        else: return None
    
    def _check_bust(self, hand):
        return self.calculate_value(hand) > 21

    #runs a single round
    def run(self, strategy:callable = None, visualize:bool = True):
        if self._finite_deck: self.deck = self._generate_deck() if len(self.deck) < int(self._initial_deck_size * self.penetration) else self.deck
        if self._performance_mode: visualize = False
        self._dealer_hand.clear()
        self.player_hand.clear()
        self.is_running = True
        self.games += 1
        self.double = False

        #Bet Logic
        if (self._bets_active and self.current_bet > 0) or not self._bets_active:
                if self._bets_active:
                    if visualize: print(f'Bankroll: {self.bankroll}')
                    if strategy is None or not callable(strategy):
                        self.current_bet = min(int(input("Enter Bet: ")), self.bankroll)
                        self.bankroll -= self.current_bet
                    if visualize: print(f'Bet: {self.current_bet}')

                #handing 2 cards to the player
                for i in range(2):
                    self.player_hand.append(self._pull_card())
                if visualize: print(f"Player: {self.player_hand} = {self.calculate_value(self.player_hand)}")
                
                #handing 2 cards to the dealer
                for i in range(2):
                    self._dealer_hand.append(self._pull_card())
                if visualize: print(f"Dealer: [/, {self._dealer_hand[1]}]")

                if self.calculate_value(self.player_hand) == 21 and self.calculate_value(self._dealer_hand) == 21:
                    if self._performance_mode: self.pushes += 1
                    else: self.player_results.append(0)
                    self.player_blackjacks += 1
                    self.dealer_blackjacks += 1
                    self.is_running = False
                    self.bankroll += self.current_bet
                    if visualize:
                        print('--Player + Dealer Blackjack!--')
                        print('-----Push-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                        print(f"EV: {self.get_player_ev()}")
                    return 0
                
                #checking if player has a blackjack
                elif self.calculate_value(self.player_hand) == 21:
                    if self._performance_mode: self.player_wins += 1
                    else: self.player_results.append(self._blackjack_payout)
                    self.player_blackjacks += 1
                    self.is_running = False
                    self.bankroll += self.current_bet + self.current_bet * self._blackjack_payout
                    self.total_profit += self.current_bet * self._blackjack_payout
                    if visualize:
                        print('--Player Blackjack!--')
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                        print(f"EV: {self.get_player_ev()}")
                    return self._blackjack_payout
                
                #checking if dealer has a blackjack
                elif self.calculate_value(self._dealer_hand) == 21:
                    if self._performance_mode: self.player_losses += 1 
                    else: self.player_results.append(-1)
                    self.dealer_blackjacks += 1
                    self.is_running = False
                    self.total_profit -= self.current_bet
                    if visualize:
                        print('--Dealer Blackjack!--')
                        print('-----Lose-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                        print(f"EV: {self.get_player_ev()}")
                    return -1

                #getting player choice
                while not self._check_bust(self.player_hand):
                    decision =  int(input("Hit(1) or Stand(0): ")) if strategy is None or not callable(strategy) else strategy(self)
                    
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
                        if (self.current_bet * 2) <= self.bankroll and len(self.player_hand) == 2:
                            self.bankroll -= self.current_bet
                            self.current_bet *= 2
                            self.double = True
                            self.player_hand.append(self._pull_card())
                            if visualize:
                                print('-Double-')
                                print(f"Player: {self.player_hand} = {self.calculate_value(self.player_hand)}")
                            break
                        continue
                            
                #checking if player got busted
                if self._check_bust(self.player_hand):
                    if self._performance_mode: self.player_losses += 1
                    else: self.player_results.append(-2) if self.double else self.player_results.append(-1)
                    self.is_running = False
                    self.total_profit -= self.current_bet
                    if visualize:
                        print(f"Dealer: {self._dealer_hand} = {self.calculate_value(self._dealer_hand)}")
                        print('--Player Bust--')
                        print('-----Lose-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                        print(f"EV: {self.get_player_ev()}")
                    return -1
                
                #dealer logic with soft 17
                else:
                    while self.calculate_value(self._dealer_hand) < 17:
                            self._dealer_hand.append(self._pull_card())
                            if visualize: print(f"Dealer: {self._dealer_hand} = {self.calculate_value(self._dealer_hand)}")
                    if self.calculate_value(self._dealer_hand) == 17 and self._dealer_hand.count(11) > 0:
                        if self._dealer_hit_17: 
                            self._dealer_hand.append(self._pull_card())
                            if visualize: print(f"Dealer: {self._dealer_hand} = {self.calculate_value(self._dealer_hand)}")
                
                #checking if dealer got busted
                if self._check_bust(self._dealer_hand):
                    if self._performance_mode: self.player_wins += 1
                    else: self.player_results.append(2) if self.double else self.player_results.append(1)
                    self.is_running = False
                    self.bankroll += self.current_bet * 2
                    self.total_profit += self.current_bet
                    if visualize:
                        print('--Dealer Bust--')
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                        print(f"EV: {self.get_player_ev()}")
                    return 1
                
                #checking if player beat dealer
                elif self.calculate_value(self.player_hand) > self.calculate_value(self._dealer_hand):
                    if self._performance_mode: self.player_wins += 1
                    else: self.player_results.append(2) if self.double else self.player_results.append(1)
                    self.is_running = False
                    self.bankroll += self.current_bet * 2
                    self.total_profit += self.current_bet
                    if visualize:
                        print('-----Win-----')
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")                        
                        print(f"EV: {self.get_player_ev()}")
                    return 1
                
                #checking if dealer beat player
                elif self.calculate_value(self.player_hand) < self.calculate_value(self._dealer_hand):
                    if self._performance_mode: self.player_losses += 1
                    else: self.player_results.append(-2) if self.double else self.player_results.append(-1)
                    self.is_running = False
                    self.total_profit -= self.current_bet
                    if visualize:
                        print('-----Lose-----')
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
                        print(f"Winrate: {self.get_win_prob(self.player_wins if self._performance_mode else (self.player_results.count(1) + self.player_results.count(2) + self.player_results.count(1.5))) * 100}%")
                        print(f"EV: {self.get_player_ev()}")
                    return 0
                

    def get_win_prob(self, wins):
        return (wins / self.games) if self.games > 0 else 0.0
    
    def get_loss_prob(self, losses):
        return (losses / self.games) if self.games > 0 else 0.0
    
    def get_push_prob(self, pushes):
        return (pushes / self.games) if self.games > 0 else 0.0
    
    def get_blackjack_prob(self, blackjacks):
        return (blackjacks / self.games) if self.games > 0 else 0.0
    
    def get_player_ev(self):
        if self._performance_mode:
            return self.total_profit / self.games if self.games > 0 else 0
        else:
            return np.mean(self.player_results) #if performance mode is active only a single EV value is returned