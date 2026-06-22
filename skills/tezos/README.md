# tezos skill

expert tezos blockchain development guidance for claude code & clawhub

## what it does

provides comprehensive guidance for building on tezos:
- smart contract patterns and security
- fa1.2 and fa2 token standards
- gas optimization techniques
- testing and deployment workflows
- common gotchas and solutions

## installation

### claude code

```bash
# clone to your skills directory
cd ~/.claude/skills
git clone https://github.com/efekucuk/tezos-skill tezos

# or download SKILL.md directly
mkdir -p ~/.claude/skills/tezos
curl -o ~/.claude/skills/tezos/SKILL.md https://raw.githubusercontent.com/efekucuk/tezos-skill/master/SKILL.md
```

### cursor

```bash
# clone to cursor skills directory
cd ~/.cursor/skills
git clone https://github.com/efekucuk/tezos-skill tezos
```

### clawhub

available on [clawhub.com](https://clawhub.com) - search for "tezos"

## usage

invoke the skill when working on tezos development:

```
/tezos help me build an fa2 nft contract
```

```
/tezos optimize gas in this contract
```

```
/tezos security checklist for this code
```

claude will load tezos-specific expertise including:
- security patterns
- token standard implementations
- gas optimization strategies
- testing approaches

## what's included

### smart contract guidance
- michelson, ligo, smartpy language selection
- common patterns (admin, pausable, upgradeability)
- security checklist (reentrancy, overflow, access control)

### token standards
- fa1.2 implementation patterns
- fa2 multi-token standard
- fa2.1 with tickets

### optimization
- gas reduction techniques
- storage optimization
- view patterns for read operations

### deployment
- testing strategy (unit, integration, simulation)
- network selection (mainnet, shadownet, ghostnet)
- deployment workflow

## works with

- [tezos mcp server](https://github.com/efekucuk/tezos-mcp) - for blockchain operations
- octez-client - official tezos cli
- ligo compiler
- smartpy compiler

## networks covered

- mainnet - production
- shadownet - primary testnet (recommended)
- ghostnet - legacy testnet (deprecated)

## requirements

none - this is a pure skill file. works with any claude-compatible editor.

for blockchain operations, use alongside:
- [tezos mcp server](https://github.com/efekucuk/tezos-mcp)
- octez-client
- ligo/smartpy compilers

## examples

see [examples/](examples/) directory for:
- fa2 token implementation
- nft marketplace contract
- dao governance patterns
- defi protocols

## verified sources

all patterns and guidance verified against:
- https://docs.tezos.com
- https://ligolang.org
- https://opentezos.com
- https://gitlab.com/tezos/tzip (official standards)

## contributing

improvements welcome. focus areas:
- additional security patterns
- more token standard examples
- advanced optimization techniques
- real-world contract patterns

## license

mit

## related

- [etherlink skill](https://github.com/efekucuk/etherlink-skill) - for tezos l2
- [tezos mcp](https://github.com/efekucuk/tezos-mcp) - blockchain operations server

## support

questions or issues: open an issue or find me on tezos discord/slack
