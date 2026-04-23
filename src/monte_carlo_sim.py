import blackjack
from tqdm import tqdm

sim = blackjack.Simulation(performance_mode=True, bankroll=100000000, finite_deck=False)

def strategy():
    sim.bet(50)
    player_val = sim.calculate_value(sim.get_player_hand())
    if player_val > 18:
        return 2 if player_val == 11 else 1
    else: return 0


for i in range(5):
    sim.run(strategy)
print(f'Bankroll: {sim.bankroll}')
print(f'EV: {sim.get_player_ev()}')
print(f'Winrate: {sim.get_win_prob(sim.player_wins)}')
print('Finished')