# Catalog Rules (spec/verify phases)

## When to apply

Always apply these rules. If `.sdd/catalog.json` is absent, initialize it first:

1. Ask the human: "Which catalog types should this project track? Examples: screens (SCR), apis (API), tables (TBL), jobs (JOB), events (EVT). Add any custom types you need."
2. Create `.sdd/catalog.json` with the chosen types, following this schema:
   ```json
   {
     "types": [
       { "id": "<type-id>", "label": "<表示名>", "id_prefix": "<PREFIX>" }
     ]
   }
   ```
   Reference schema: `vendor/ai-sdd-guide/catalog/schema/catalog.schema.json`
3. Commit with message: `chore: initialize sdd catalog`
4. Proceed with the normal catalog flow below.

## During spec phase — register as planned

When writing or updating `specs/<feature>/spec.md`, identify any new items that belong
in a catalog type (e.g. a new page → screens, a new endpoint → apis, a new table → tables).

For each new item:

1. Read `.sdd/catalog.json` to confirm the type exists and get its `id_prefix`.
2. Determine the next sequential ID:
   - Open `docs/design/<type>/index.md` (create it from `catalog/templates/index.md.example` if absent).
   - Find the highest existing `<id_prefix>-NNN` number in the table. Next ID = that number + 1, zero-padded to 3 digits.
   - If no entries exist yet, start at 001.
3. Choose a slug: lowercase, hyphen-separated summary of the item name (e.g. `login`, `post-auth-login`, `users`).
4. Add a row to `docs/design/<type>/index.md`:
   ```
   | <id_prefix>-NNN | <title> | planned | [<feature>](../../specs/<feature>/spec.md) | [→](<id_prefix>-NNN-<slug>.md) |
   ```
5. Create `docs/design/<type>/<id_prefix>-NNN-<slug>.md` from `catalog/templates/definition.md.example`:
   - Set `id`, `title`, `status: planned`, `feature`, `updated: <today YYYY-MM-DD>`.
   - Write `## 仕様` content based on what the spec says about this item.

Never reuse an ID. Deprecated entries still occupy their number.

## During verify phase — confirm entries

After `sdd-reviewer` confirms the implementation:

1. In `docs/design/<type>/index.md`, change the matching row's status from `planned` to `confirmed`.
2. In `docs/design/<type>/<id>.md`:
   - Change frontmatter `status: planned` to `status: confirmed`.
   - Update `updated:` to today's date.
   - If the implementation diverged from the spec, revise `## 仕様` to match the actual state.

## Deprecating entries

When a spec removes or replaces a catalogued item:

1. In `index.md`, change the entry's status to `deprecated`.
2. In the definition file, change frontmatter `status` to `deprecated` and update `updated:`.
3. Do NOT delete the file — deprecated entries are kept for history.

## ID rules

- Format: `<id_prefix>-NNN` (e.g. SCR-001, API-012, TBL-003).
- Zero-pad to 3 digits minimum (001, 002, ..., 099, 100).
- IDs are sequential and permanent. Never reuse, even after deprecation.
- Scan `index.md` for the highest existing number to find the next available ID.
