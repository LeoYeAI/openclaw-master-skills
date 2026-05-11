# Language Resolution Policy

## Priority Order

Resolve target language with this strict priority:

1. `explicit_output_language_request`
2. `target_language_parameter`
3. `session_language_preference`
4. `prompt_language_detection`
5. `source_material_dominant_language`
6. `default_fallback_language` (`en-US`)

## Control Fields

- `target_language` (BCP-47 recommended, for example `fr-FR`, `ja-JP`, `zh-CN`)
- `bilingual_output` (`true|false`)
- `term_policy` (`preserve|translate|mixed`)
- `quote_policy` (`translate_only|original_plus_translation`)

## Rules

- Do not restrict supported languages to a fixed list.
- If output language is explicit, source-language distribution must not override it.
- Learner-facing script text must follow resolved target language unless `bilingual_output` is true.
