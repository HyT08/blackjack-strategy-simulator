import matplotlib.pyplot as plt
import numpy as np

def monte_carlo(simulation, strategy, mc_runs: int = 100, bj_rounds: int = 10000, plot: bool = True, plot_points: int = 500):
    if plot_points > bj_rounds:
        plot_points = bj_rounds

    step = max(1, bj_rounds // plot_points)

    histories = []
    evs = []
    player_edges = []
    winrates = []
    lossrates = []
    pushrates = []
    blackjacks = []
    max_drawdowns = []
    min_bankrolls = []
    total_profits = []
    total_bets = []
    avg_bets = []
    rois = []
    ruins = 0

    for i in range(mc_runs):
        sim = simulation.clone(performance_mode=True)
        run = sim.run
        history = []
        initial_bankroll = sim.initial_bankroll
        ruined = False

        for j in range(bj_rounds):
            # skip heavy logic after ruin
            if not ruined:
                run(strategy)
                bankroll = sim.bankroll

                if bankroll <= 0:
                    ruined = True
                    ruins += 1
                    bankroll = 0
            else:
                bankroll = 0

            if plot:
                if j % step == 0:
                    history.append(bankroll - initial_bankroll)

        evs.append(sim.get_player_ev())
        player_edges.append(sim.get_player_edge())
        winrates.append(sim.get_win_prob(sim.player_wins))
        lossrates.append(sim.get_loss_prob(sim.player_losses))
        pushrates.append(sim.get_push_prob())
        blackjacks.append(sim.get_blackjack_prob(sim.player_blackjacks))
        max_drawdowns.append(sim.max_drawdown)
        min_bankrolls.append(sim.min_bankroll)
        total_profit = sim.total_profit
        total_profits.append(total_profit)
        total_bets.append(sim.total_bet)
        rois.append((total_profit) / initial_bankroll)
        avg_bets.append(sim.get_avg_bet())

        if plot:
            histories.append(history)

    if plot and histories:
        for h in histories:
            plt.plot(h, alpha=0.5, linewidth=1)

        plt.plot(np.mean(histories, axis=0), linewidth=2, label="Mean")
        plt.legend()

    print("--------Monte Carlo Simulation Results--------")

    ev_mean = np.mean(evs)
    ev_std = np.std(evs)
    ci = 1.96 * ev_std / np.sqrt(len(evs))

    print(f'Total Rounds played: {bj_rounds * mc_runs}')
    print(f"EV (Profit/Hand): {round(ev_mean, 2)}")
    print(f"EV Std Dev: {round(ev_std, 2)}")
    print(f"EV 95% CI: [{round(ev_mean - ci, 2)}, {round(ev_mean + ci, 2)}]")
    print(f"Global Edge: {round((np.sum(total_profits) / np.sum(total_bets))* 100, 2)}%")
    print(f"Avg Edge: {round(np.mean(player_edges) * 100, 2)}%")
    print(f"House Edge: {- round((np.sum(total_profits) / np.sum(total_bets))* 100, 2)}%")
    print(f"Avg Bet: {round(np.mean(avg_bets), 2)}")
    print(f"Avg Total Profit: {round(np.mean(total_profits), 2)}")
    print(f"ROI: {round(np.mean(rois) * 100, 2)}%")
    print(f"RoR: {round((ruins / mc_runs) * 100, 2)}")
    print(f"Winrate: {round(np.mean(winrates) * 100, 2)}%")
    print(f"Effective Winrate: {round(np.mean(winrates) / (1 - np.mean(pushrates)) * 100, 2)}%")
    print(f"Lossrate: {round(np.mean(lossrates) * 100, 2)}%")
    print(f"Pushrate: {round(np.mean(pushrates) * 100, 2)}%")
    print(f"Blackjacks: {round(np.mean(blackjacks) * 100, 2)}%")
    print(f"Avg Min Bankroll: {round(np.mean(min_bankrolls), 2)}")
    print(f"Worst Min Bankroll: {round(np.min(min_bankrolls), 2)}")
    print(f"Max Drawdown: {round(min(max_drawdowns) * 100, 2)}%")
    print(f"Avg Max Drawdown: {round(np.mean(max_drawdowns) * 100, 2)}%")