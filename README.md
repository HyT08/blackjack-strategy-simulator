# Blackjack-Strategy-Simulator

A Python-based Blackjack simulation and strategy evaluation framework.

## The project supports both:
- an interactive Blackjack Simulation for manual play and small-scale testing
- a Monte Carlo simulation system for evaluating strategies over a large number of games

## Features
- Monte Carlo simulation for large-scale analysis
- Expected Value (EV) calculation
- Finite and infinite deck support
- Configurable number of decks and deck penetration
- Betting and doubling functionality
- Support for custom strategies

The Goal of this project is to create a flexible and extensible framework for analyzing Blackjack strategies under realistic conditions. 
This project also serves as a foundation for further projects in the field of Quantitative Finance.

## Installation
pip install -r requirements.txt

## Building your own strategy
Open strategies.py and write your own strategy with the following structure:
```python
class Strategy:
    def bet(self, sim):
        #your bet logic
    def play(self, sim):
        #your gameplay logic
```
### Toolset for building your strategy:
#### Conditions:
```python
sim.get_player_hand_val()
#-> returns the total value of your hand
sim.player_aces
#-> returns the number of aces in your hand (useful to detect soft hands)
sim.player_card_count
#-> returns the number of cards in your hand
sim._get_dealer_hand_val(full_hand=False)
#-> returns the visible value of the dealer hand (only upcard value if not revealed)
sim._get_dealer_hand_val(full_hand=True)
#-> returns the full value of the dealer's hand
sim._dealer_upcard
#-> returns the revealed card of the dealer
sim.bankroll
#-> returns your current bankroll
sim.current_bet
#-> returns your current bet size
sim.total_bet
#-> returns the total amount you have bet so far
sim.games
#-> returns the number of games played
sim.phase
#-> returns the current phase of the game ("bet", "game", or None)
```

#### Actions:
```python
sim.bet(amount)
#-> place a bet before the round starts
return 0
#-> Stand
return 1
#-> Hit
return 2
#-> Double (only allowed on the first two cards and if bankroll allows it)
```
At leat one hit or stand return and a bet (if bets=active in the simulation, look at Testing for further info) are needed to test the strategy

#### Performance / Stats (after simulation):
```python
sim.get_player_ev()
#-> returns the expected value (profit per hand)
sim.get_win_prob(sim.player_wins)
#-> returns win probability
sim.get_loss_prob(sim.player_losses)
#-> returns loss probability
sim.get_push_prob()
#-> returns push probability
sim.get_blackjack_prob(sim.player_blackjacks)
#-> returns blackjack probability
```

## Testing
### Testing with a Monte Carlo Simulation
- Open the notebook testing.ipynp
- Configure the parameters for the blackjack game here:
```python
simulation = src.blackjack.Simulation(performance_mode=True, finite_deck=False, 
                           num_of_decks=6, penetration=0.8 , 
                           bets_active=True, bankroll=10000, 
                           dealer_hit_17=True, blackjack_payout=1.5)
```
performance_mode=True and finite_deck=False are highly recommended if you want do a Monte Carlo Simulation
- Choose the strategy you want to simulate with here:
```python
strategy = src.strategies.YourStrategyName()
```
- Configure the Parameters for the Monte Carlo Simulation here:
```python
src.monte_carlo.monte_carlo(simulation, strategy, mc_runs=100, bj_rounds=1000, plot=True, plot_points=500)
```
- Run the import cell
- Run the Simulation cell every time you want a new Monte Carlo Simulation
  
Tip: If you put a new strategy in strategies.py clear all outputs, restart the Kernel and again run the import cell

If everything worked correctly your Cell Outputs should look like this:
```bash
--------Monte Carlo Simulation Results--------
Total Rounds played: 100000
EV (Profit/Hand): -0.34
EV Std Dev: 1.64
EV 95% CI: [-0.66, -0.02]
Global Edge: -0.76%
Avg Edge: -0.78%
House Edge: 0.76%
Avg Bet: 44.48
Avg Total Profit: -338.81
ROI: -3.39%
RoR: 0.0
Winrate: 43.48%
Effective Winrate: 47.44%
Lossrate: 48.18%
Pushrate: 8.34%
Blackjacks: 4.63%
Avg Min Bankroll: 8429.31
Worst Min Bankroll: 4839.72
Max Drawdown: -52.96%
Avg Max Drawdown: -20.4%
```
<img width="572" height="413" alt="image" src="https://github.com/user-attachments/assets/1632e1ea-7a89-4d2e-898a-14464efdf4a2" />
