from __future__ import annotations


class HiLoCardCountingStrategy:
    """
    Callable strategy compatible with Simulation.run(strategy).
    - When a round starts (sim.is_running == False): sets bet size.
    - During player turn: returns 0/1/2 (stand/hit/double).
    """

    def __init__(self, simulation, base_bet=50, max_spread=8):
        self.sim = simulation
        self.base_bet = max(1, int(base_bet))
        self.max_spread = max(1, int(max_spread))

        self.running_count = 0
        self.cards_seen = 0
        self._counted_cards_this_round = set()

        self._initial_deck_size = getattr(self.sim, "_initial_deck_size", 52)
        self._deck_qty = max(1, getattr(self.sim, "_deck_qty", 1))

    def __call__(self):
        # Round start: place bet and reset per-round card cache.
        if not self.sim.is_running:
            self._counted_cards_this_round.clear()
            bet_amount = self._bet_for_count()
            self.sim.bet(bet_amount)
            return None

        self._update_count_from_visible_cards()
        return self._player_decision()

    def _count_delta(self, card_value):
        # Hi-Lo: 2-6 = +1, 7-9 = 0, 10/A(11) = -1
        if 2 <= card_value <= 6:
            return 1
        if card_value in (10, 11):
            return -1
        return 0

    def _observe_card_once(self, card):
        # Use (round_id, index, value) style id based on local counter size.
        # We only need uniqueness inside the round to avoid double counting.
        card_id = (len(self._counted_cards_this_round), card)
        if card_id in self._counted_cards_this_round:
            return
        self._counted_cards_this_round.add(card_id)
        self.running_count += self._count_delta(card)
        self.cards_seen += 1

    def _update_count_from_visible_cards(self):
        # Player cards are always visible.
        player_hand = self.sim.get_player_hand() or []
        for idx, card in enumerate(player_hand):
            card_id = ("p", idx, card)
            if card_id not in self._counted_cards_this_round:
                self._counted_cards_this_round.add(card_id)
                self.running_count += self._count_delta(card)
                self.cards_seen += 1

        # Dealer card is upcard during player action; full hand later.
        dealer_view = self.sim.get_dealer_hand()
        if dealer_view is None:
            return
        if isinstance(dealer_view, list):
            for idx, card in enumerate(dealer_view):
                card_id = ("d", idx, card)
                if card_id not in self._counted_cards_this_round:
                    self._counted_cards_this_round.add(card_id)
                    self.running_count += self._count_delta(card)
                    self.cards_seen += 1
        else:
            card_id = ("d_up", 0, dealer_view)
            if card_id not in self._counted_cards_this_round:
                self._counted_cards_this_round.add(card_id)
                self.running_count += self._count_delta(dealer_view)
                self.cards_seen += 1

    def _true_count(self):
        if getattr(self.sim, "_finite_deck", False):
            cards_remaining = max(1, self._initial_deck_size - self.cards_seen)
            decks_remaining = max(cards_remaining / 52.0, 0.25)
        else:
            # Infinite shoe approximation: use deck_qty as denominator scale.
            decks_remaining = float(self._deck_qty)
        return self.running_count / decks_remaining

    def _bet_for_count(self):
        true_count = self._true_count()
        units = 1 + max(0, int(true_count))
        units = min(units, self.max_spread)
        return self.base_bet * units

    def _can_double(self):
        return len(self.sim.get_player_hand()) == 2 and (self.sim.current_bet * 2) <= self.sim.bankroll

    def _dealer_upcard(self):
        dealer_view = self.sim.get_dealer_hand()
        if isinstance(dealer_view, list):
            return dealer_view[1] if len(dealer_view) >= 2 else None
        return dealer_view

    def _player_decision(self):
        player_hand = self.sim.get_player_hand()
        player_value = self.sim.calculate_value(player_hand)
        dealer_up = self._dealer_upcard()

        # Bust safety.
        if player_value >= 21:
            return 0

        # Simple doubling rules.
        if self._can_double():
            if player_value == 11 and dealer_up != 11:
                return 2
            if player_value == 10 and dealer_up in (2, 3, 4, 5, 6, 7, 8, 9):
                return 2
            if player_value == 9 and dealer_up in (3, 4, 5, 6):
                return 2

        # Basic total rules (hard/soft simplified).
        if player_value <= 11:
            return 1
        if player_value >= 17:
            return 0

        # 12-16: stand vs weak dealer, otherwise hit.
        if dealer_up in (2, 3, 4, 5, 6):
            return 0
        return 1


def make_hilo_strategy(simulation, base_bet=50, max_spread=8):
    """
    Factory helper for notebook usage:
        strategy = make_hilo_strategy(sim)
        sim.run(strategy)
    """
    return HiLoCardCountingStrategy(
        simulation=simulation,
        base_bet=base_bet,
        max_spread=max_spread,
    )


def test(simulation):
    """Backward compatible simple strategy."""
    if not simulation.is_running:
        simulation.bet(500)
        return None

    value = simulation.calculate_value(simulation.get_player_hand())
    if value < 17:
        return 1
    return 0

def stand(simulation):
    simulation.bet(50)