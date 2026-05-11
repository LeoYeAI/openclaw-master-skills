declare module 'porter-stemmer' {
  export function stemmer(word: string): string;
  export function memoizingStemmer(word: string): string;
}
