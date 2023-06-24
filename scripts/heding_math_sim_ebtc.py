from random import random

"""
  Basic Hedging Math Sim based on:
  https://lambert-guillaume.medium.com/how-to-deploy-delta-neutral-liquidity-in-uniswap-or-why-euler-finance-is-a-game-changer-for-lps-1d91efe1e8ac

  Adapted to use Balancer assuming
  CapitalEfficiency(Bal) >= CapitalEfficiency(UniV2)
"""
MAX_BPS = 10_000

MAX_VOLATILITY = 9900 ## 99% swing is max


MAX_APR_FOR_BORROW_BPS = 0 ## It costs nothing to borrow

COST_OF_TRADE_BPS = 55 ## .55% as bigger trade WILL require 1Inch, UniV3 PI is above 10% for 100 ETH

LTV_BPS = 8500 ## .9090% is max | 110 CR

LIQUIDATION_TRESHOLD = 9090.9090909

INITIAL_DEPOSIT_ETH = 100
ETH_DECIMALS = 18

## NOTE: Copy paste latest from here: https://data.chain.link/ethereum/mainnet/crypto-eth/comp-eth
BTC_ETH_RATIO = 13 ## 1 BTC = 13 ETH

## We use this initial K to simulate price impact that makes sense
## NOTE: Real liquidty with added zeros to soften price impact
## TODO: We may not need any of this just use ratios
UNIV2_START_ETH =  2612361562405349369717
UNIV2_START_BTC = 16099996237  * 10 ** 18 / 10 ** 8
UNIV2_K = UNIV2_START_ETH * UNIV2_START_BTC


def sim(volatility_bps):
  """
    volatility_bps. How much to lose, and How much to gain for the sim to check if we're within bounds
  """
  print("volatility_bps", volatility_bps)
  
  initial_amount = INITIAL_DEPOSIT_ETH * 10 ** ETH_DECIMALS

  print("Starting Price", 1 / BTC_ETH_RATIO)


  ## Deposit 2/3 into COMP
  deposit_into_cdp = initial_amount * 2 / 3

  liquid_amount = initial_amount - deposit_into_cdp

  btc_borrowable_in_eth = deposit_into_cdp * LTV_BPS / MAX_BPS

  ## Borrow only half to reduce risk || 50% Hedge
  btc_we_will_borrow_in_eth = btc_borrowable_in_eth / 2

  all_btc_borrowable = btc_we_will_borrow_in_eth / BTC_ETH_RATIO

  ## If this ever reaches LIQUIDATION_TRESHOLD we get liquidated
  borrow_ratio = btc_we_will_borrow_in_eth / deposit_into_cdp * 10_000

  ## We did not get liquidated yet
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)
  print("Starting Borrow Ratio ", borrow_ratio)

  ## Assume LP at 50/50
  ## We do have more than we borrowed meaning we can afford to LP
  ## NOTE: We are not as capital efficient as possible, 
  ## if you know how, I got a job for you -> alex@badger.com
  assert(liquid_amount > btc_we_will_borrow_in_eth)

  eth_in_lp = btc_we_will_borrow_in_eth
  btc_in_lp = all_btc_borrowable
  print("eth_in_lp", eth_in_lp)
  print("btc_in_lp", btc_in_lp)

  ## Scenario 1, loss of X%
  loss_in_eth = UNIV2_START_ETH * volatility_bps / MAX_BPS
  print("loss_in_eth", loss_in_eth)

  ## Compute new Ratios ## NOTE: Assumes UniV2
  ## Increase 
  new_eth_in_lp = UNIV2_START_ETH - loss_in_eth
  print("new_eth_in_lp", new_eth_in_lp)

  new_btc_in_lp = UNIV2_K / new_eth_in_lp
  print("new_btc_in_lp", new_btc_in_lp)

  new_price = new_btc_in_lp / new_eth_in_lp
  print("new_price", new_price)

  ## Compute new Health Factor
  borrow_ratio = all_btc_borrowable / new_price / deposit_into_cdp * 10_000
  print("Loss Borrow Ratio ", borrow_ratio)
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)

  ## Scenario 2, gain of X%
  gain_in_eth = UNIV2_START_ETH * volatility_bps / MAX_BPS
  print("gain_in_eth", gain_in_eth)

  ## Increase 
  new_eth_in_lp = UNIV2_START_ETH + gain_in_eth
  print("new_eth_in_lp", new_eth_in_lp)

  new_btc_in_lp = UNIV2_K / new_eth_in_lp
  print("new_btc_in_lp", new_btc_in_lp)

  new_price = new_btc_in_lp / new_eth_in_lp
  print("new_price", new_price)

  ## Compute new Health Factor
  borrow_ratio = all_btc_borrowable / new_price / deposit_into_cdp * 10_000
  print("Gain Borrow Ratio ", borrow_ratio)
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)

  ## TODO: Extend

  






ROUNDS = 10_000


def main():
  max = 0
  for i in range(ROUNDS):
    try:
      vol = round(random() * MAX_VOLATILITY) + 1
      sim(vol)

      if vol > max:
        max = vol
    except:
        x = 0 ## Nothing

  print("max", max)

main()