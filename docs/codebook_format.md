# Codebook format

The editable codebook lives at `app/codebook/examples/codebook.example.yml`.

It contains:

- `codebook`: name, version, description, theoretical framework.
- `framework_settings`: analytic orientation, coding orientation, theme orientation, epistemological position, semantic/latent setting, inductive/deductive setting.
- `features`: editable feature schemas with allowed values and extraction hints.
- `themes`: editable themes with analytical definitions, inclusion criteria, exclusion criteria, examples, counterexamples, indicators, and codes.
- `memo_prompts`: prompts for familiarisation, coding, and theme review.

Indicators may be simple keywords, phrases, or regex expressions prefixed with `regex:`.
