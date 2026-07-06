#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { named } = parseArgs(process.argv);
const period = named.period ?? "30d";

const data = await tmrFetch("GET", `/dashboard/revenue-series?period=${period}`);
console.log(JSON.stringify(data, null, 2));
