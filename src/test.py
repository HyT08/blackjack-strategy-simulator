#file to test your strategy
import blackjack
from tqdm import tqdm

game = blackjack.Simulation(performance_mode=True, finite_deck=True, bets_active=True, bankroll=100000000) 

def strategy():
    game.bet(50)
    if game.calculate_value(game.get_player_hand()) < 17:
        return 2 if game.calculate_value(game.get_player_hand()) == 10 else 1
    else: 
        return 0


choice = 2

#1. semi-auto
if choice == 1:
    while True:
        round = game.run(strategy)
        if input("Press Enter for Next Round (x to exit): ") == 'x' or game.bankroll == 0: break

#2. auto
elif choice == 2:
    rounds = 1000000
    for i in range(rounds):
        round = game.run(strategy)
    print(f'Bankroll: {game.bankroll}')
    print(f'EV: {game.get_player_ev()}')
    print(f'Winrate: {game.get_win_prob(game.player_wins)}')