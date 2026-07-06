#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/dashboard/overview");
console.log(JSON.stringify(data, null, 2));
