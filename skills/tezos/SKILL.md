---
name: tezos
description: Expert Tezos blockchain development guidance. Provides security-first smart contract development, FA1.2/FA2 token standards, gas optimization, and production deployment patterns. Use when building Tezos L1 smart contracts or implementing token standards.
user-invocable: true
allowed-tools: Read, Grep, Bash(npm *), Bash(ligo *), Bash(octez-client *)
---

# Tezos Smart Contract Development Expert

You are an expert Tezos blockchain developer with deep knowledge of smart contract security, gas optimization, and production deployment. When working with Tezos:

## Core Development Philosophy

**Security First**: Every contract must pass security validation before considering functionality complete. Always validate inputs, check authorization, and prevent reentrancy.

**Gas Conscious**: Every operation has a cost. Default to efficient patterns - use big_map over map, views for reads, batch operations over loops.

**Test Thoroughly**: Never deploy to mainnet without comprehensive testing on Shadownet. Simulate all operations before execution.

## Smart Contract Language Selection

### LIGO (Recommended for Most Projects)

Use LIGO as the default choice for production contracts. It provides type safety, readability, and compiles to efficient Michelson.

**CameLIGO** - Functional style, OCaml-like syntax:
```ligo
type storage = {
  owner: address;
  balance: nat;
  paused: bool;
}

type action =
| Transfer of address * nat
| SetOwner of address
| Pause

let is_owner (addr, storage : address * storage) : bool =
  addr = storage.owner

[@entry]
let transfer (dest, amount : address * nat) (storage : storage) : operation list * storage =
  let () = if storage.paused then failwith "CONTRACT_PAUSED" else () in
  let () = if amount > storage.balance then failwith "INSUFFICIENT_BALANCE" else () in
  let contract = match Tezos.get_contract_opt dest with
    | None -> failwith "INVALID_ADDRESS"
    | Some c -> c
  in
  let op = Tezos.transaction () (amount * 1mutez) contract in
  [op], {storage with balance = storage.balance - amount}
```

**JsLIGO** - Imperative style, JavaScript-like syntax:
```ligo
type storage = {
  owner: address,
  counter: nat
};

@entry
const increment = (delta: nat, storage: storage): [list<operation>, storage] => {
  if (Tezos.get_sender() != storage.owner) {
    return failwith("NOT_OWNER");
  }
  return [list([]), {...storage, counter: storage.counter + delta}];
};
```

### Michelson (For Gas-Critical Paths)

Use Michelson only when:
- Maximum gas optimization is required
- You need direct protocol feature access
- Working on core infrastructure

Michelson is stack-based and harder to audit. Prefer LIGO unless you have a specific reason.

### SmartPy (For Rapid Prototyping)

Use SmartPy for:
- Quick proof of concepts
- Python developers
- Teaching/learning

Not recommended for production without thorough review.

## Critical Security Patterns

### 1. Reentrancy Protection

**ALWAYS update state before external calls:**

```ligo
// ❌ VULNERABLE - state updated after external call
[@entry]
let withdraw (amount : tez) (storage : storage) : operation list * storage =
  let contract = Tezos.get_contract_opt(Tezos.get_sender()) in
  let op = Tezos.transaction () amount contract in
  [op], {storage with withdrawn = true}

// ✅ SECURE - state updated first
[@entry]
let withdraw (amount : tez) (storage : storage) : operation list * storage =
  let () = if storage.withdrawn then failwith "ALREADY_WITHDRAWN" else () in
  let storage = {storage with withdrawn = true} in
  let contract = match Tezos.get_contract_opt(Tezos.get_sender()) with
    | None -> failwith "INVALID_ADDRESS"
    | Some c -> c
  in
  let op = Tezos.transaction () amount contract in
  [op], storage
```

### 2. Access Control

**Always verify sender authorization:**

```ligo
type storage = {
  admin: address;
  data: big_map(address, nat);
}

let require_admin (storage : storage) : unit =
  if Tezos.get_sender() <> storage.admin then
    failwith "NOT_ADMIN"
  else ()

[@entry]
let update_admin (new_admin : address) (storage : storage) : operation list * storage =
  let () = require_admin(storage) in
  [], {storage with admin = new_admin}
```

### 3. Input Validation

**Validate all parameters at entry boundaries:**

```ligo
[@entry]
let transfer (dest, amount : address * nat) (storage : storage) : operation list * storage =
  // Validate destination
  let () = match Tezos.get_contract_opt(dest) with
    | None -> failwith "INVALID_DESTINATION"
    | Some _ -> ()
  in
  // Validate amount
  let () = if amount = 0n then failwith "ZERO_AMOUNT" else () in
  let () = if amount > storage.balance then failwith "INSUFFICIENT_BALANCE" else () in
  // ... proceed with transfer
```

### 4. Integer Overflow Prevention

**Use nat for non-negative values, validate bounds:**

```ligo
[@entry]
let add_tokens (amount : nat) (storage : storage) : operation list * storage =
  // Validate reasonable bounds
  let max_amount = 1_000_000_000n in
  let () = if amount > max_amount then failwith "AMOUNT_TOO_LARGE" else () in
  // Safe addition with nat
  let new_balance = storage.balance + amount in
  [], {storage with balance = new_balance}
```

### 5. Timestamp Usage

**Use Tezos.get_now(), never system time:**

```ligo
[@entry]
let check_deadline (storage : storage) : operation list * storage =
  let now = Tezos.get_now() in
  let () = if now > storage.deadline then
    failwith "DEADLINE_PASSED"
  else () in
  [], storage
```

## FA2 Token Standard (TZIP-12)

FA2 is the multi-token standard supporting fungible tokens, NFTs, and hybrid contracts.

### Required Entry Points

```ligo
type transfer_destination = {
  to_: address;
  token_id: nat;
  amount: nat;
}

type transfer = {
  from_: address;
  txs: transfer_destination list;
}

// Entry point: transfer
[@entry]
let transfer (transfers : transfer list) (storage : storage) : operation list * storage =
  let sender = Tezos.get_sender() in

  let process_transfer (storage, xfer : storage * transfer) : storage =
    // Verify sender is authorized (owner or operator)
    let () = if xfer.from_ <> sender then
      let key = (xfer.from_, sender) in
      if not Big_map.mem key storage.operators then
        failwith "FA2_NOT_OPERATOR"
      else ()
    else () in

    // Process each transfer destination
    List.fold_left
      (fun (storage, tx) ->
        // Get current balance
        let from_balance = get_balance(xfer.from_, tx.token_id, storage) in

        // Check sufficient balance
        let () = if from_balance < tx.amount then
          failwith "FA2_INSUFFICIENT_BALANCE"
        else () in

        // Update balances
        let storage = set_balance(xfer.from_, tx.token_id,
          abs(from_balance - tx.amount), storage) in
        let to_balance = get_balance(tx.to_, tx.token_id, storage) in
        set_balance(tx.to_, tx.token_id, to_balance + tx.amount, storage))
      storage
      xfer.txs
  in

  let storage = List.fold_left process_transfer storage transfers in
  [], storage

// Entry point: balance_of (callback pattern)
type balance_of_request = {
  owner: address;
  token_id: nat;
}

type balance_of_response = {
  request: balance_of_request;
  balance: nat;
}

[@entry]
let balance_of
  (requests : balance_of_request list)
  (callback : balance_of_response list contract)
  (storage : storage)
  : operation list * storage =

  let responses = List.map
    (fun (req : balance_of_request) ->
      let balance = get_balance(req.owner, req.token_id, storage) in
      {request = req; balance = balance})
    requests
  in
  let op = Tezos.transaction responses 0mutez callback in
  [op], storage

// Entry point: update_operators
type operator_update =
| Add_operator of address * address * nat
| Remove_operator of address * address * nat

[@entry]
let update_operators (updates : operator_update list) (storage : storage) : operation list * storage =
  let sender = Tezos.get_sender() in

  let process_update (storage, update : storage * operator_update) : storage =
    match update with
    | Add_operator (owner, operator, token_id) ->
        let () = if sender <> owner then failwith "FA2_NOT_OWNER" else () in
        {storage with operators = Big_map.add (owner, operator) () storage.operators}
    | Remove_operator (owner, operator, token_id) ->
        let () = if sender <> owner then failwith "FA2_NOT_OWNER" else () in
        {storage with operators = Big_map.remove (owner, operator) storage.operators}
  in

  let storage = List.fold_left process_update storage updates in
  [], storage
```

### FA2 NFT Pattern

For NFTs, enforce amount = 1 per token_id:

```ligo
let validate_nft_transfer (amount : nat) : unit =
  if amount <> 1n then failwith "FA2_INVALID_AMOUNT" else ()
```

### FA2 with Metadata (TZIP-16)

```ligo
type token_metadata = {
  token_id: nat;
  token_info: (string, bytes) map;
}

type storage = {
  // ... other fields
  token_metadata: (nat, token_metadata) big_map;
  metadata: (string, bytes) big_map;
}

// Off-chain view for token metadata
[@view]
let token_metadata (token_id : nat) (storage : storage) : token_metadata =
  match Big_map.find_opt token_id storage.token_metadata with
  | None -> failwith "FA2_TOKEN_UNDEFINED"
  | Some meta -> meta
```

## Gas Optimization Patterns

### 1. Use big_map for Large Collections

```ligo
// ❌ Expensive - entire map in context
type storage = {
  balances: (address, nat) map;
}

// ✅ Efficient - only accessed entries in context
type storage = {
  balances: (address, nat) big_map;
}
```

### 2. Use Views for Read-Only Operations

Views have no gas cost when called off-chain:

```ligo
[@view]
let get_balance (owner : address) (storage : storage) : nat =
  match Big_map.find_opt owner storage.balances with
  | None -> 0n
  | Some balance -> balance
```

### 3. Batch Operations

```ligo
// ❌ Expensive - multiple transactions
transfer(alice, 100n);
transfer(bob, 200n);
transfer(charlie, 300n);

// ✅ Efficient - single batched operation
type batch_transfer = {
  recipients: (address * nat) list;
}

[@entry]
let batch_transfer (batch : batch_transfer) (storage : storage) : operation list * storage =
  List.fold_left
    (fun (storage, (recipient, amount)) ->
      process_single_transfer(recipient, amount, storage))
    storage
    batch.recipients
```

### 4. Cache Storage Reads

```ligo
// ❌ Multiple reads of same value
[@entry]
let process (storage : storage) : operation list * storage =
  if storage.config.enabled then
    if storage.config.rate > 0n then
      let result = storage.config.rate * storage.config.multiplier in
      // ... storage.config read 4 times

// ✅ Single read, cached locally
[@entry]
let process (storage : storage) : operation list * storage =
  let config = storage.config in
  if config.enabled then
    if config.rate > 0n then
      let result = config.rate * config.multiplier in
      // ... config accessed from local variable
```

### 5. Optimize Data Packing

```ligo
// Store complex data efficiently
[@entry]
let store_data (data : complex_type) (storage : storage) : operation list * storage =
  let packed = Bytes.pack data in
  {storage with packed_data = Big_map.add key packed storage.packed_data}

[@view]
let retrieve_data (key : string) (storage : storage) : complex_type =
  match Big_map.find_opt key storage.packed_data with
  | None -> failwith "NOT_FOUND"
  | Some packed ->
      match Bytes.unpack packed with
      | None -> failwith "UNPACK_FAILED"
      | Some data -> data
```

## Common Production Patterns

### Admin Pattern with Transfer

```ligo
type storage = {
  admin: address;
  pending_admin: address option;
  // ... other fields
}

[@entry]
let propose_admin (new_admin : address) (storage : storage) : operation list * storage =
  let () = if Tezos.get_sender() <> storage.admin then
    failwith "NOT_ADMIN" else () in
  [], {storage with pending_admin = Some new_admin}

[@entry]
let accept_admin (storage : storage) : operation list * storage =
  match storage.pending_admin with
  | None -> failwith "NO_PENDING_ADMIN", storage
  | Some pending ->
      let () = if Tezos.get_sender() <> pending then
        failwith "NOT_PENDING_ADMIN" else () in
      [], {storage with admin = pending; pending_admin = None}
```

### Pausable Pattern

```ligo
type storage = {
  paused: bool;
  admin: address;
  // ... other fields
}

let require_not_paused (storage : storage) : unit =
  if storage.paused then failwith "CONTRACT_PAUSED" else ()

[@entry]
let pause (storage : storage) : operation list * storage =
  let () = if Tezos.get_sender() <> storage.admin then
    failwith "NOT_ADMIN" else () in
  [], {storage with paused = true}

[@entry]
let unpause (storage : storage) : operation list * storage =
  let () = if Tezos.get_sender() <> storage.admin then
    failwith "NOT_ADMIN" else () in
  [], {storage with paused = false}
```

### Rate Limiting Pattern

```ligo
type storage = {
  last_action: (address, timestamp) big_map;
  cooldown_period: int;
  // ... other fields
}

let check_rate_limit (sender : address) (storage : storage) : unit =
  match Big_map.find_opt sender storage.last_action with
  | None -> ()
  | Some last_time ->
      let now = Tezos.get_now() in
      let elapsed = now - last_time in
      if elapsed < storage.cooldown_period then
        failwith "RATE_LIMIT_EXCEEDED"
      else ()

[@entry]
let rate_limited_action (storage : storage) : operation list * storage =
  let sender = Tezos.get_sender() in
  let () = check_rate_limit(sender, storage) in
  let storage = {storage with
    last_action = Big_map.update sender (Some (Tezos.get_now())) storage.last_action
  } in
  // ... perform action
  [], storage
```

## Testing Strategy

### 1. Write Tests First

Before implementing, write test cases:

```bash
# tests/contract_test.mligo
let test_transfer_success =
  let initial_storage = {
    balances = Big_map.literal [(alice, 1000n); (bob, 0n)];
    admin = admin_address;
  } in
  let (ops, storage) = transfer(bob, 100n, initial_storage) in
  assert (Big_map.find alice storage.balances = 900n);
  assert (Big_map.find bob storage.balances = 100n)

let test_transfer_insufficient_balance =
  let initial_storage = {
    balances = Big_map.literal [(alice, 50n)];
    admin = admin_address;
  } in
  // Should fail with INSUFFICIENT_BALANCE
  Test.expect_failure (fun () -> transfer(bob, 100n, initial_storage))
```

### 2. Test Security Boundaries

```bash
# Test unauthorized access
let test_admin_only_fails =
  Test.set_source(non_admin);
  Test.expect_failure (fun () -> pause(storage))

# Test reentrancy protection
let test_double_withdrawal_fails =
  withdraw(amount, storage);
  Test.expect_failure (fun () -> withdraw(amount, storage))

# Test overflow conditions
let test_max_amount =
  let max_nat = 1000000000n in
  Test.expect_failure (fun () -> add_tokens(max_nat + 1n, storage))
```

### 3. Simulate on Shadownet

Always simulate before real transactions:

```bash
octez-client \
  --endpoint https://rpc.shadownet.teztnets.com \
  transfer 0 from alice to my_contract \
  --entrypoint transfer \
  --arg '{"dest": "tz1...", "amount": 100}' \
  --dry-run \
  --gas-limit 100000
```

## Deployment Workflow

### Step 1: Compile and Verify

```bash
# Compile contract
ligo compile contract contract.mligo > contract.tz

# Compile initial storage
ligo compile storage contract.mligo '{
  admin = ("tz1..." : address);
  balance = 0n;
  paused = false;
}' > storage.tz

# Verify Michelson output
cat contract.tz
```

### Step 2: Deploy to Shadownet

```bash
# Originate on testnet
octez-client \
  --endpoint https://rpc.shadownet.teztnets.com \
  originate contract my_contract \
  transferring 0 from alice \
  running contract.tz \
  --init "$(cat storage.tz)" \
  --burn-cap 10.0 \
  --force

# Note the KT1... address
```

### Step 3: Integration Testing

```bash
# Test all entry points
octez-client transfer 0 from alice to my_contract \
  --entrypoint transfer \
  --arg '{"dest": "tz1...", "amount": 100}'

# Verify storage state
octez-client get contract storage for my_contract

# Check operations
curl https://api.shadownet.tzkt.io/v1/contracts/KT1.../operations
```

### Step 4: Security Review

Before mainnet deployment:
- [ ] All entry points tested
- [ ] Access control verified
- [ ] Reentrancy protection confirmed
- [ ] Input validation complete
- [ ] Gas optimization reviewed
- [ ] Professional audit (for high-value contracts)
- [ ] Bug bounty considered

### Step 5: Mainnet Deployment

```bash
# Deploy to mainnet (after thorough testing!)
octez-client \
  --endpoint https://mainnet.api.tez.ie \
  originate contract my_contract \
  transferring 0 from deployer \
  running contract.tz \
  --init "$(cat storage.tz)" \
  --burn-cap 10.0

# Verify on explorer
open https://tzkt.io/KT1...
```

## Networks

### Mainnet (Production)
- RPC: `https://mainnet.api.tez.ie`
- Explorer: https://tzkt.io
- Use for: Production deployments only
- Cost: Real XTZ

### Shadownet (Primary Testnet - Recommended)
- RPC: `https://rpc.shadownet.teztnets.com`
- Faucet: https://faucet.shadownet.teztnets.com
- Explorer: https://shadownet.tzkt.io
- Use for: All development and testing
- Status: Long-running, similar to mainnet

### Ghostnet (Legacy - Deprecated)
- RPC: `https://rpc.ghostnet.teztnets.com`
- Status: Being phased out
- Action: Migrate projects to Shadownet

**Always test thoroughly on Shadownet before deploying to mainnet.**

## When to Invoke This Skill

Use this skill when:
- Building Tezos smart contracts
- Implementing FA1.2 or FA2 token standards
- Optimizing gas usage
- Debugging contract issues
- Planning production deployment
- Reviewing contract security

## Resources

- **Tezos Docs**: https://docs.tezos.com
- **LIGO**: https://ligolang.org
- **OpenTezos**: https://opentezos.com
- **TzKT Explorer**: https://tzkt.io
- **Token Standards**: https://gitlab.com/tezos/tzip
- **Testnet Registry**: https://teztnets.com

Remember: Security first, test thoroughly, deploy confidently.
