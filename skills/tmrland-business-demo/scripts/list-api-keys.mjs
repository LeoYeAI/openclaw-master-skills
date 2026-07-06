#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/api-keys");
console.log(JSON.stringify(data, null, 2));
