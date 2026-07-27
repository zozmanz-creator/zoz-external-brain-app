# Zlachny Chisinau data protocol

## Rule
No venue is published as verified without a source URL and verification date. Unknown values stay `null`; they are never guessed.

## Statuses
- `verified`: official source confirms the main details; coordinates have a map source.
- `partial`: the venue exists, but at least one important field is conflicting or incomplete.
- `demo`: interface-only record; hidden by default.

## Required fields
`id`, `name`, `type`, `categories`, `district`, `address`, `coordinates`, `hoursLabel`, `schedule`, `status`, `sources`.

## Verification hierarchy
1. Official venue website or official social profile.
2. Official ticketing/cinema page or current city/event directory.
3. Map source for coordinates.
4. Review directory only as supporting evidence, never as the sole source for critical facts.

## Images
Until an official venue image is saved with permission, use a stock image only with `imageStatus: illustrative`; the UI must show “ФОТО-ИЛЛЮСТРАЦИЯ”.

## Updating
Set `verifiedAt` to the actual review date and add every source as `{label, url}`. Conflicts go into `verificationNote` and force `status: partial`.
