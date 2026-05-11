#!/usr/bin/env npx tsx

// 抑制 Promise.all 中未处理的 rejection（已由 main catch 处理）
process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection:", reason)
})

import { setJsonMode, error } from "../src/lib/output.js"
import { hasFlag, getFlagValue, removeFlags, removeFlagWithValue } from "../src/lib/args.js"

async function main() {
  let args = process.argv.slice(2)

  // 全局 flags
  if (hasFlag(args, "--json")) setJsonMode(true)
  if (hasFlag(args, "--version")) {
    const pkg = await import("../package.json", { with: { type: "json" } })
    console.log(pkg.default.version)
    return
  }

  // --network 覆盖
  const networkOverride = getFlagValue(args, "--network")
  if (networkOverride) {
    process.env.FOMO3D_NETWORK = networkOverride
    args = removeFlagWithValue(args, "--network")
  }

  args = removeFlags(args, "--json")

  if (hasFlag(args, "--help", "-h") || args.length === 0) {
    args = removeFlags(args, "--help", "-h")
    // 如果有子命令带 --help，仍然路由到对应命令
    if (args.length === 0) {
      printHelp()
      return
    }
  }

  const [command, subcommand] = args
  const rest = args.slice(1)

  switch (command) {
    case "setup": {
      const { setup } = await import("../src/commands/setup.js")
      return setup(rest)
    }
    case "wallet": {
      const { wallet } = await import("../src/commands/wallet.js")
      return wallet(rest)
    }
    case "status": {
      const { status } = await import("../src/commands/status.js")
      return status(rest)
    }
    case "player": {
      const { player } = await import("../src/commands/player.js")
      return player(rest)
    }
    case "purchase": {
      const { purchase } = await import("../src/commands/purchase.js")
      return purchase(rest)
    }
    case "exit": {
      const { exit } = await import("../src/commands/exit.js")
      return exit(rest)
    }
    case "settle": {
      const { settle } = await import("../src/commands/settle.js")
      return settle(rest)
    }
    case "end-round": {
      const { endRound } = await import("../src/commands/end-round.js")
      return endRound(rest)
    }
    case "faucet": {
      const { faucet } = await import("../src/commands/faucet.js")
      return faucet(rest)
    }
    case "buy": {
      const { buy } = await import("../src/commands/buy.js")
      return buy(rest)
    }
    case "sell": {
      const { sell } = await import("../src/commands/sell.js")
      return sell(rest)
    }
    case "token-info": {
      const { tokenInfo } = await import("../src/commands/token-info.js")
      return tokenInfo(rest)
    }
    case "slot": {
      const slotRest = args.slice(2)
      switch (subcommand) {
        case "status": {
          const { slotStatus } = await import("../src/commands/slot-status.js")
          return slotStatus(slotRest)
        }
        case "spin": {
          const { slotSpin } = await import("../src/commands/slot-spin.js")
          return slotSpin(slotRest)
        }
        case "cancel": {
          const { slotCancel } = await import("../src/commands/slot-cancel.js")
          return slotCancel(slotRest)
        }
        case "deposit": {
          const { slotDeposit } = await import("../src/commands/slot-deposit.js")
          return slotDeposit(slotRest)
        }
        case "claim": {
          const { slotClaim } = await import("../src/commands/slot-claim.js")
          return slotClaim(slotRest)
        }
        default:
          console.error(`Unknown slot command: ${subcommand ?? "(none)"}`)
          console.error("Available: status, spin, cancel, deposit, claim")
          process.exit(1)
      }
      break
    }
    case "pred": {
      const predRest = args.slice(2)
      switch (subcommand) {
        case "config": {
          const { predConfig } = await import("../src/commands/pred-config.js")
          return predConfig(predRest)
        }
        case "market": {
          const { predMarket } = await import("../src/commands/pred-market.js")
          return predMarket(predRest)
        }
        case "position": {
          const { predPosition } = await import("../src/commands/pred-position.js")
          return predPosition(predRest)
        }
        case "bet": {
          const { predBet } = await import("../src/commands/pred-bet.js")
          return predBet(predRest)
        }
        case "exit": {
          const { predExit } = await import("../src/commands/pred-exit.js")
          return predExit(predRest)
        }
        case "claim": {
          const { predClaim } = await import("../src/commands/pred-claim.js")
          return predClaim(predRest)
        }
        case "create": {
          const { predCreate } = await import("../src/commands/pred-create.js")
          return predCreate(predRest)
        }
        case "oracle": {
          const { predOracle } = await import("../src/commands/pred-oracle.js")
          return predOracle(predRest)
        }
        case "optimistic": {
          const { predOptimistic } = await import("../src/commands/pred-optimistic.js")
          return predOptimistic(predRest)
        }
        case "settle-oracle": {
          const { predSettleOracle } = await import("../src/commands/pred-settle-oracle.js")
          return predSettleOracle(predRest)
        }
        case "propose": {
          const { predPropose } = await import("../src/commands/pred-propose.js")
          return predPropose(predRest)
        }
        case "dispute": {
          const { predDispute } = await import("../src/commands/pred-dispute.js")
          return predDispute(predRest)
        }
        case "finalize": {
          const { predFinalize } = await import("../src/commands/pred-finalize.js")
          return predFinalize(predRest)
        }
        case "resolve": {
          const { predResolve } = await import("../src/commands/pred-resolve.js")
          return predResolve(predRest)
        }
        default:
          console.error(`Unknown pred command: ${subcommand ?? "(none)"}`)
          console.error("Available: config, market, position, bet, exit, claim, create, oracle, optimistic, settle-oracle, propose, dispute, finalize, resolve")
          process.exit(1)
      }
      break
    }
    default:
      console.error(`Unknown command: ${command}`)
      printHelp()
      process.exit(1)
  }
}

function printHelp() {
  console.log(`
fomo3d — Play Fomo3D and Slot Machine on BNB Chain (BSC)

USAGE:
  fomo3d <command> [options]

SETUP:
  setup                         Configure wallet and network

INFO:
  wallet                        Show BNB + token balances
  status                        Game round status, countdown, pools
  player [--address 0x...]      Player shares, earnings, pending

TESTNET:
  faucet                        Claim 10000 test FOMO tokens

GAME ACTIONS:
  purchase --shares <n>         Buy shares (auto-approves token)
  exit                          Exit game, claim dividends
  settle                        Settle after round ends + claim prize
  end-round                     End expired round

TOKEN TRADING (FLAP):
  buy --amount <bnb_wei>        Buy FOMO with BNB
  sell --amount <token_wei>     Sell FOMO tokens for BNB
  sell --percent <bps>          Sell by % (10000=100%, 5000=50%)
  token-info                    Token status, price, balances

SLOT MACHINE:
  slot status                   Slot machine status and stats
  slot spin --bet <n>           Spin (requires BNB for VRF fee)
  slot cancel                   Cancel timed-out spin
  slot deposit --amount <n>     Deposit tokens to prize pool
  slot claim                    Claim slot dividends

PREDICTION MARKET:
  pred config                   Global prediction config
  pred market --id <n>          Market details
  pred position --id <n>        Your position in a market
  pred bet --id <n> --side <yes|no|draw> --amount <wei>
                                Place a bet
  pred exit --id <n> --side <yes|no|draw>
                                Exit a side, claim dividends
  pred claim --id <n>           Claim settlement after resolve
  pred create --title <str> --end-time <ts> --bond <wei> --challenge-period <s> [--draw]
                                Create optimistic market
  pred oracle --id <n>          Oracle market price info
  pred optimistic --id <n>      Optimistic settlement status
  pred settle-oracle --id <n>   Settle oracle market
  pred propose --id <n> --outcome <yes|no|draw>
                                Propose outcome (bond required)
  pred dispute --id <n>         Dispute proposal (bond required)
  pred finalize --id <n>        Finalize after challenge period
  pred resolve --id <n> --outcome <yes|no|draw> [--proposer-wins]
                                Arbiter resolves dispute

FLAGS:
  --json                        JSON output (for AI agents)
  --network testnet|mainnet     Override network
  --help                        Show help
  --version                     Show version
`)
}

main().catch((err) => {
  error(err instanceof Error ? err.message : String(err))
  process.exit(1)
})
