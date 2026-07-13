export function stringifyJson(payload) {
    return JSON.stringify(payload);
}
export function printJson(payload) {
    console.log(stringifyJson(payload));
}
export function printErrorJson(payload) {
    console.error(stringifyJson(payload));
}
export function exitWithCode(code) {
    process.exit(code);
}
