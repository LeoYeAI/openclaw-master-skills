#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/dashboard/agent-status");
console.log(JSON.stringify(data, null, 2));
