#file to test your strategy manually
import sys
import os
sys.path.append(os.path.abspath("../src"))
import strategies
import blackjack

#Configure the parameters for the blackjack game:
sim = blackjack.Simulation(performance_mode=True, finite_deck=True, 
                           num_of_decks=6, penetration=0.8 , 
                           bets_active=True, bankroll=10000, 
                           dealer_hit_17=True, blackjack_payout=1.5)

strategy = strategies.Example()

choice = 2

#1. semi-auto
if choice == 1:
    while True:
        round = sim.run(strategy)
        if input("Press Enter for Next Round (x to exit): ") == 'x' or sim.bankroll == 0: break

#2. auto
elif choice == 2:
    rounds = 1000000
    for i in range(rounds):
        round = sim.run(strategy)
    print(f'Bankroll: {sim.bankroll}')
    print(f'EV: {sim.get_player_ev()}')
    print(f'Winrate: {sim.get_win_prob(sim.player_wins)}')
