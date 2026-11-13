# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the "Label in our tracker" column to match whatever vocabulary you actually use.

## Theme labels (not triage roles)

Orthogonal to triage state; skills don't set these. Apply one when an issue is
created, if it belongs to a theme. Slugs match `ROADMAP.md`.

| Label | Stage |
|---|---|
| `theme:llm-mechanics` | 1 |
| `theme:model-apis` | 2 |
| `theme:evals` | 3 |
| `theme:context-and-retrieval` | 4 |
| `theme:agents` | 5 |
| `theme:production` | 6 |
| `theme:ai-assisted-engineering` | none |
| `theme:leading-teams` | none |

Site-skeleton and repo-infrastructure work gets no theme label.
