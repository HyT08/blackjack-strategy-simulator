#basic strategy structure
class Strategy:
    def bet(self, sim):
        #your bet logic
        pass
    def play(self, sim):
        #your gameplay logic
        pass

class MyStrategy:
    def bet(self, sim):
        sim.bet(50)

    def play(self, sim):
        return 1 if sim.player_hand_val < 17 else 0


# Alternative simpler strategy if you want less complexity
class SimpleHiLoCounter:
    """
    Simplified Hi-Lo counter with basic strategy and linear betting spread.
    Easier to understand and modify.
    """
    
    HI_LO = {2:1, 3:1, 4:1, 5:1, 6:1, 7:0, 8:0, 9:0, 10:-1, 11:-1}
    
    def __init__(self, base_unit=25, spread=10):
        self.base_unit = base_unit
        self.spread = spread  # Max bet = base_unit * spread
        self.running_count = 0
    
    def _get_true_count(self, sim):
        if not sim._finite_deck:
            return 0
        # Estimate from deck
        remaining = len(sim.deck) / 52.0
        if remaining < 0.5:
            remaining = 0.5
        
        # Quick deck estimation: count remaining high vs low cards
        deck_count = sum(self.HI_LO.get(c, 0) for c in sim.deck)
        # Invert: if deck has many high cards, true count is negative
        true_count = -deck_count / remaining
        return true_count
    
    def bet(self, sim):
        tc = self._get_true_count(sim)
        
        if tc <= 0:
            units = 1
        elif tc < 1:
            units = 2
        elif tc < 2:
            units = 4
        elif tc < 3:
            units = 6
        elif tc < 4:
            units = 8
        else:
            units = self.spread
        
        bet = self.base_unit * units
        bet = min(bet, sim.bankroll * 0.02)  # Max 2% of bankroll
        bet = max(bet, self.base_unit)
        sim.bet(bet)
    
    def play(self, sim):
        val = sim.player_hand_val
        up = sim._dealer_upcard
        soft = sim.player_aces > 0
        tc = self._get_true_count(sim)
        
        # Basic strategy with one key deviation: 16 vs 10
        if val == 16 and not soft and up == 10 and tc > 0:
            return 0  # Stand with any positive count
        
        # Standard basic strategy
        if soft:
            if val >= 19: return 0
            if val == 18:
                if up in [2,7,8]: return 0
                if up in [3,4,5,6]: return 2 if sim.player_card_count == 2 else 0
                return 1
            if val == 17 and up in [3,4,5,6]: return 2 if sim.player_card_count == 2 else 1
            return 1
        
        if val >= 17: return 0
        if val in [13,14,15,16] and up in [2,3,4,5,6]: return 0
        if val == 12 and up in [4,5,6]: return 0
        if val == 11: return 2 if sim.player_card_count == 2 else 1
        if val == 10 and up not in [10,11]: return 2 if sim.player_card_count == 2 else 1
        if val == 9 and up in [3,4,5,6]: return 2 if sim.player_card_count == 2 else 1
        return 1
    
