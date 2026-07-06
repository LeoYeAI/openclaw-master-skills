#!/usr/bin/env node
import { tmrFetch } from "./_lib.mjs";

const data = await tmrFetch("GET", "/notifications/preferences");
console.log(JSON.stringify(data, null, 2));
