import blackjack

game = blackjack.Simulation(finite_deck=True, num_of_decks=1, bets_active=False) 

def strategy():
    if game.get_player_hand_val() < 17:
        print('Hit')
        return 2 if game.get_player_hand_val() == 10 or 11 else 1
    else: 
        print('Stand')
        return 0


choice = 1

#1. semi-auto
if choice == 1:
    while True:
        round = game.run(strategy)
        if input("Press Enter for Next Round (x to exit): ") == 'x': break

#2. auto
elif choice == 2:
    rounds = 100
    for i in range(rounds):
        round = game.run(strategy)