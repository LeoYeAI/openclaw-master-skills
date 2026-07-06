#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/dashboard/agent-health-history");
console.log(JSON.stringify(data, null, 2));
