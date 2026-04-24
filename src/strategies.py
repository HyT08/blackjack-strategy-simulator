def test(simulation):
    simulation.bet(50)
    value = simulation.get_player_hand_val()
    if value < 17:
        return simulation.hit()
    return simulation.stand()