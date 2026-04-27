#basic strategy structure
class Strategy:
    def bet(self, sim):
        #your bet logic
        pass
    def play(self, sim):
        #your gameplay logic
        pass


#example strategy
class Example(Strategy):
    
    def __init__(self):
        self.count = 0

    def update_count(self, sim):
        hand = sim.get_player_hand()
        if hand is None:
            return
        
        cards = hand + [sim.get_dealer_hand()]
        
        for c in cards:
            if 2 <= c <= 6:
                self.count += 1
            elif c >= 10:
                self.count -= 1

    def bet(self, sim):
        bankroll = sim.get_bankroll()

        if self.count > 5:
            bet = int(bankroll * 0.03)
        elif self.count > 2:
            bet = int(bankroll * 0.02)
        else:
            bet = int(bankroll * 0.005)

        sim.bet(max(1, bet))

    def play(self, sim):
        self.update_count(sim)

        player = sim.get_player_hand_val()
        dealer = sim.get_dealer_hand()

        if player >= 17:
            return 0

        if sim.player_card_count == 2:
            if player == 11:
                return 2
            if player == 10 and dealer < 10:
                return 2
            if player == 9 and 3 <= dealer <= 6:
                return 2

        if 13 <= player <= 16:
            return 0 if dealer <= 6 else 1

        if player == 12:
            return 0 if 4 <= dealer <= 6 else 1

        return 1
