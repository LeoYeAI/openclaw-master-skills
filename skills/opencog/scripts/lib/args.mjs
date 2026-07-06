// CLI argument utilities shared by all scripts.
//
// parseArgs   — minimal --key value / --key=value / --flag parser
// requireArgs — exits with an error listing any missing required flags
// getChainFromArgs — reads --chain or CHAIN env (currently unused by scripts)

// Minimal CLI arg parser. Supports --key value and --key=value.
export function parseArgs(argv = process.argv.slice(2)) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (!arg.startsWith("--")) continue;
    const eqIdx = arg.indexOf("=");
    if (eqIdx !== -1) {
      args[arg.slice(2, eqIdx)] = arg.slice(eqIdx + 1);
    } else {
      const next = argv[i + 1];
      if (next === undefined || next.startsWith("--")) {
        args[arg.slice(2)] = true;
      } else {
        args[arg.slice(2)] = argv[++i];
      }
    }
  }
  return args;
}

export function requireArgs(args, required) {
  const missing = required.filter(k => !(k in args));
  if (missing.length) {
    console.error(`Missing required args: ${missing.map(k => `--${k}`).join(", ")}`);
    process.exit(1);
  }
}

export function getChainFromArgs(args) {
  return args.chain || process.env.CHAIN || null;
}
