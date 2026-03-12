# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Tapio project.

An ADR captures a significant architectural decision made during the project: what was decided, why it was decided that way, and what the consequences are. ADRs are written at the time of the decision and remain in the repository as a permanent record — including decisions that are later superseded.

## Why ADRs?

- **Onboarding** — New contributors can understand not just what the architecture is, but why it is that way
- **Avoiding re-litigation** — Decisions that were already considered don't need to be re-argued from scratch
- **Accountability** — Trade-offs are made explicit rather than hidden in commit messages or tribal knowledge

## File naming

ADRs are numbered sequentially and given a short descriptive slug:

```text
NNNN-short-description.md
```

For example: `0001-cloudflare-crawler.md`

## Statuses

Each ADR carries one of the following statuses:

| Status                                     | Meaning                                                |
| ------------------------------------------ | ------------------------------------------------------ |
| **Proposed**                               | Under discussion, not yet adopted                      |
| **Accepted**                               | Decision has been adopted                              |
| **Deprecated**                             | No longer relevant but retained for historical context |
| **Superseded by [NNNN](NNNN-filename.md)** | Replaced by a later decision                           |

## Creating a new ADR

Copy `_template.md`, increment the number, fill in each section, and open a pull request for review.
