import blackjack as bj

game = bj.Blackjack(finite_deck=True, num_of_decks=1, bets_active=False) 

def strategy():
    return 1 if game.get_player_hand() < 17 else 0

choice = 2

#1. semi auto
if choice == 1:
    while True:
        round = game.run(strategy)
        if round == 1.5: print('--Blackjack--')
        print('----Win----' if round >= 1 else '----Lose----')
        print(f"Winrate: {game.get_win_prob() * 100}%")
        print(f"EV: {game.get_ev()}")
        if input("Press Enter for Next Round (x to exit): ") == 'x':
            break

#2. auto
elif choice == 2:
    rounds = 100

    for i in range(rounds):
        round = game.run(strategy)
    print('--------------------')
    print(f"Winrate: {game.get_win_prob() * 100}%")
    print(f"EV: {game.get_ev()}")