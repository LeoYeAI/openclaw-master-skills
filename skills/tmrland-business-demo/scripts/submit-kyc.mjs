#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.name || !named["id-type"] || !named["id-number"]) {
  console.error("Usage: submit-kyc.mjs --name \"...\" --id-type passport|national_id|driver_license --id-number \"...\"");
  process.exit(2);
}

const body = {
  name: named.name,
  id_type: named["id-type"],
  id_number: named["id-number"],
};

const data = await tmrFetch("POST", "/wallet/kyc", body);
console.log(JSON.stringify(data, null, 2));
