import blackjack as bj

game = bj.Blackjack(finite_deck=True, num_of_decks=1, bets_active=False) 

def strategy():
    return 1 if game.get_player_hand() < 17 else 0

while True:
    round = game.run(strategy)
    if round == 1.5: print('--Blackjack--')
    print('----Win----' if round >= 1 else '----Lose----')
    print(f"Winrate: {game.get_winrate()}%")
    print(f"EV: {game.get_ev()}")
    input("Press Enter for Next Round: ")
