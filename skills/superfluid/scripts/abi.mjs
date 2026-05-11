#!/usr/bin/env node
// Superfluid ABI Resolver
// Self-contained — no npm install required. Imports JSON ABIs from the @sfpro/sdk
// package at runtime.
//
// Usage:
//   bunx -p @sfpro/sdk bun abi.mjs <contract>                 Full JSON ABI for a contract
//   bunx -p @sfpro/sdk bun abi.mjs <contract> <function>      Single function/event/error fragment
//   bunx -p @sfpro/sdk bun abi.mjs list                       List all available contracts
//
// Output: JSON to stdout. Errors to stderr.

// Contract name → SDK module + export name.
// Module "main" = @sfpro/sdk/abi, others = @sfpro/sdk/abi/<module>.
const ABI_MAP = {
  // @sfpro/sdk/abi (main)
  CFAv1Forwarder:                 { module: "main",       export: "cfaForwarderAbi" },
  GDAv1Forwarder:                 { module: "main",       export: "gdaForwarderAbi" },
  SuperfluidPool:                 { module: "main",       export: "gdaPoolAbi" },
  SuperToken:                     { module: "main",       export: "superTokenAbi" },
  // @sfpro/sdk/abi/core
  Superfluid:                     { module: "core",       export: "hostAbi" },
  ConstantFlowAgreementV1:        { module: "core",       export: "cfaAbi" },
  GeneralDistributionAgreementV1: { module: "core",       export: "gdaAbi" },
  InstantDistributionAgreementV1: { module: "core",       export: "idaAbi" },
  SuperTokenFactory:              { module: "core",       export: "superTokenFactoryAbi" },
  BatchLiquidator:                { module: "core",       export: "batchLiquidatorAbi" },
  TOGA:                           { module: "core",       export: "togaAbi" },
  Governance:                     { module: "core",       export: "governanceAbi" },
  // @sfpro/sdk/abi/automation
  AutoWrapManager:                { module: "automation",  export: "autoWrapManagerAbi" },
  AutoWrapStrategy:               { module: "automation",  export: "autoWrapStrategyAbi" },
  FlowScheduler:                  { module: "automation",  export: "flowSchedulerAbi" },
  VestingSchedulerV3:             { module: "automation",  export: "vestingSchedulerV3Abi" },
  // @sfpro/sdk/abi/sup
  Fontaine:                       { module: "sup",         export: "fontaineAbi" },
  FluidLocker:                    { module: "sup",         export: "lockerAbi" },
  FluidLockerFactory:             { module: "sup",         export: "lockerFactoryAbi" },
  FluidEPProgramManager:          { module: "sup",         export: "programManagerAbi" },
  StakingRewardController:        { module: "sup",         export: "stakingRewardControllerAbi" },
  SUPToken:                       { module: "sup",         export: "supTokenAbi" },
  SUPVestingFactory:              { module: "sup",         export: "vestingFactoryAbi" },
};

// Shorthand aliases → canonical name.
const ALIASES = {
  cfaforwarder: "CFAv1Forwarder",
  gdaforwarder: "GDAv1Forwarder",
  pool: "SuperfluidPool",
  gdapool: "SuperfluidPool",
  supertoken: "SuperToken",
  token: "SuperToken",
  host: "Superfluid",
  cfa: "ConstantFlowAgreementV1",
  gda: "GeneralDistributionAgreementV1",
  ida: "InstantDistributionAgreementV1",
  supertokenfactory: "SuperTokenFactory",
  factory: "SuperTokenFactory",
  batchliquidator: "BatchLiquidator",
  liquidator: "BatchLiquidator",
  toga: "TOGA",
  governance: "Governance",
  autowrapmanager: "AutoWrapManager",
  autowrap: "AutoWrapManager",
  autowrapstrategy: "AutoWrapStrategy",
  flowscheduler: "FlowScheduler",
  vestingschedulerv3: "VestingSchedulerV3",
  vestingscheduler: "VestingSchedulerV3",
  vesting: "VestingSchedulerV3",
  fontaine: "Fontaine",
  locker: "FluidLocker",
  fluidlocker: "FluidLocker",
  lockerfactory: "FluidLockerFactory",
  fluidlockerfactory: "FluidLockerFactory",
  programmanager: "FluidEPProgramManager",
  fluidepprogrammanager: "FluidEPProgramManager",
  stakingrewardcontroller: "StakingRewardController",
  staking: "StakingRewardController",
  suptoken: "SUPToken",
  sup: "SUPToken",
  supvestingfactory: "SUPVestingFactory",
  vestingfactory: "SUPVestingFactory",
};

function resolveContract(query) {
  // Exact match on canonical name (case-insensitive).
  const byCanonical = Object.keys(ABI_MAP).find(k => k.toLowerCase() === query.toLowerCase());
  if (byCanonical) return byCanonical;
  // Alias match.
  return ALIASES[query.toLowerCase()] ?? null;
}

async function loadModule(module) {
  return import(sdkImportPath(module));
}

function sdkImportPath(module) {
  return module === "main" ? "@sfpro/sdk/abi" : `@sfpro/sdk/abi/${module}`;
}

const out = o => console.log(JSON.stringify(o, null, 2));
const [command, ...args] = process.argv.slice(2);

switch (command) {
  case "list": {
    const entries = Object.entries(ABI_MAP).map(([name, { module, export: exp }]) => ({
      contract: name,
      sdkImport: sdkImportPath(module),
      sdkExport: exp,
    }));
    out(entries);
    break;
  }

  case undefined:
  case "help":
  case "--help":
  case "-h": {
    console.error(`Superfluid ABI Resolver — imports JSON ABIs from @sfpro/sdk

Commands:
  <contract>               Full JSON ABI for a contract
  <contract> <function>    Single function/event/error fragment by name
  list                     List all available contracts with SDK import info

Contracts:
  ${Object.keys(ABI_MAP).join(", ")}

Aliases:
  cfa, gda, ida, host, pool, token, factory, toga, autowrap, vesting, liquidator, ...

Examples:
  bunx -p @sfpro/sdk bun abi.mjs CFAv1Forwarder
  bunx -p @sfpro/sdk bun abi.mjs cfa
  bunx -p @sfpro/sdk bun abi.mjs SuperToken transfer
  bunx -p @sfpro/sdk bun abi.mjs list`);
    process.exit(0);
    break;
  }

  default: {
    const name = resolveContract(command);
    if (!name) {
      // Check if it's a known contract not in the SDK.
      const notInSdk = ["CFASuperAppBase", "SuperTokenV1Library"];
      const match = notInSdk.find(n => n.toLowerCase() === command.toLowerCase());
      if (match) {
        console.error(`Error: ${match} is not available in @sfpro/sdk (${match === "CFASuperAppBase" ? "abstract base contract" : "Solidity library"}).`);
        console.error(`Refer to the Rich ABI YAML: references/contracts/${match}.abi.yaml`);
      } else {
        console.error(`Error: Unknown contract "${command}".`);
        console.error(`Run "bunx -p @sfpro/sdk bun abi.mjs list" to see available contracts.`);
      }
      process.exit(1);
    }

    const entry = ABI_MAP[name];
    const mod = await loadModule(entry.module);
    const abi = mod[entry.export];

    if (!abi) {
      console.error(`Error: Export "${entry.export}" not found in SDK module "${entry.module}".`);
      process.exit(1);
    }

    const fnName = args[0];
    if (fnName) {
      const fragments = abi.filter(item => item.name?.toLowerCase() === fnName.toLowerCase());
      if (!fragments.length) {
        console.error(`Error: No ABI entry named "${fnName}" in ${name}.`);
        console.error(`Hint: Names are case-insensitive. The ABI has ${abi.filter(i => i.name).map(i => i.name).filter((v, i, a) => a.indexOf(v) === i).length} named entries.`);
        process.exit(1);
      }
      out(fragments.length === 1 ? fragments[0] : fragments);
    } else {
      out({ contract: name, sdkImport: sdkImportPath(entry.module), sdkExport: entry.export, abi });
    }
    break;
  }
}
