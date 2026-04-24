import matplotlib.pyplot as plt
import numpy as np

def monte_carlo(simulation, strategy, mc_runs: int = 100, bj_rounds: int = 10000, plot: bool = True, plot_points: int = 500):
    if plot_points > bj_rounds:
        plot_points = bj_rounds

    step = max(1, bj_rounds // plot_points)

    histories = []
    evs = []
    winrates = []
    lossrates = []
    pushrates = []
    blackjacks = []
    max_drawdowns = []
    min_bankrolls = []
    total_profits = []
    total_bets = []
    rois = []
    ruins = 0

    for i in range(mc_runs):
        sim = simulation.clone(performance_mode=True)
        run = sim.run
        history = [0]
        max_dd = 0
        peak = sim.bankroll
        min_bankroll = sim.bankroll
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

                continue

            min_bankroll = min(min_bankroll, bankroll)

            # max drawdown
            peak = max(peak, bankroll)
            dd = (peak - bankroll) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

            # sampling for plot
            if plot:
                if j % step == 0:
                    history.append(bankroll - initial_bankroll)

        evs.append(sim.get_player_ev())
        winrates.append(sim.get_win_prob(sim.player_wins))
        lossrates.append(sim.get_loss_prob(sim.player_losses))
        pushrates.append(sim.get_push_prob())
        blackjacks.append(sim.get_blackjack_prob(sim.player_blackjacks))
        max_drawdowns.append(max_dd)
        min_bankrolls.append(min_bankroll)
        final_bankroll = sim.bankroll
        total_profits.append(final_bankroll - initial_bankroll)
        total_bets.append(sim.total_bet)
        rois.append((final_bankroll - initial_bankroll) / initial_bankroll)

        if plot:
            histories.append(history)

    print("Finished")

    if plot and histories:
        for h in histories:
            plt.plot(h, alpha=0.5, linewidth=0.5)

        plt.plot(np.mean(histories, axis=0), linewidth=2, label="Mean")
        plt.legend()

    print("--------Monte Carlo Simulation Results--------")

    ev_mean = np.mean(evs)
    ev_std = np.std(evs)
    ci = 1.96 * ev_std / np.sqrt(len(evs))

    print(f"EV (Profit/Hand): {round(ev_mean, 2)}")
    print(f"EV Std Dev: {round(ev_std, 2)}")
    print(f"EV 95% CI: [{round(ev_mean - ci, 2)}, {round(ev_mean + ci, 2)}]")
    print(f'House Edge: {- round((np.sum(total_profits) / np.sum(total_bets))* 100, 2)}%')
    print(f'Avg Bet: {np.sum(total_bets) / (mc_runs * bj_rounds)}')
    print(f"Avg Total Profit: {np.mean(total_profits)}")
    print(f"ROI: {round(np.mean(rois) * 100, 2)}%")
    print(f"RoR: {round((ruins / mc_runs) * 100, 2)}")
    print(f"Winrate: {round(np.mean(winrates) * 100, 2)}%")
    print(f"Effective Winrate: {round(np.mean(winrates) / (1 - np.mean(pushrates)) * 100, 2)}%")
    print(f"Lossrate: {round(np.mean(lossrates) * 100, 2)}%")
    print(f"Pushrate: {round(np.mean(pushrates) * 100, 2)}%")
    print(f"Blackjacks: {round(np.mean(blackjacks) * 100, 2)}%")
    print(f"Avg Min Bankroll: {np.mean(min_bankrolls)}")
    print(f"Worst Min Bankroll: {np.min(min_bankrolls)}")
    print(f"Max Drawdown: {-round(max(max_drawdowns) * 100, 2)}%")
    print(f"Avg Max Drawdown: {-round(np.mean(max_drawdowns) * 100, 2)}%")