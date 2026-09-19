# Contributing

This file overrides the [organisation default](https://github.com/greencalculus/.github/blob/main/CONTRIBUTING.md).

Contributions are welcome, including from people who have never contributed to open source before. Three of the open issues are labelled `good first issue` and each names the files to change and how to check your own work.

## Setup

There isn't one. Two files, the standard library, Python 3.9+.

```bash
git clone https://github.com/greencalculus/gwp-basis-check
cd gwp-basis-check
python3 gwp_basis_check.py --self-test
```

That runs in under a second and needs no network, no API key and no dependencies.

## The one rule that matters

**A false positive is worse than a missed error.**

Every finding this tool emits is, in effect, a claim that someone else's published number is wrong. Get that wrong and you have sent a correction to a project that was right — and the people most likely to be flagged are the ones who cared enough to label their columns in the first place.

So the self-test has nine cases and **six of them are negatives**:

| | must stay silent because |
|---|---|
| a correct three-report table | nothing is wrong with it |
| an EU F-Gas table using AR4 | the regulation mandates AR4 |
| SF₆ AR6 = 24,300 and CH₄ fossil AR5 = 30 | sources genuinely disagree; *our* value is the contested one |
| CO₂ | identical under every report |
| HFC-507A with AR4 = AR5 = 3,985 | the two reports really do publish the same number |
| bare `CH4` | AR6 publishes 27.0, 29.8 and 27.9 depending on origin |

A change that makes any of those fire will not be merged, however much coverage it adds. If your change needs a new negative case to stay honest, add one.

## Data changes beat code changes

Most of what this tool knows lives in `gwp_reference.json`, not in Python:

- **Adding a gas** — add it to `values`. No code change. ([#2](https://github.com/greencalculus/gwp-basis-check/issues/2))
- **Adding a spelling** the tool should recognise — add it to `aliases`. No code change.
- **Adding an assessment report**, when AR7 lands — append it to `bases` and add its values. No code change; CI asserts this stays true.

If you find yourself editing a regex to add a gas or a report, something has gone wrong — say so in an issue.

## Sourcing a number

Every value must come from a **named primary source**: IPCC AR6 Table 7.SM.7, or GHG Protocol *"Global Warming Potential Values"* v2.0 (August 2024), with the table. Say in the PR where you read it.

This matters more here than in most projects. A wrong reference value does not produce a wrong answer for one user — it produces a confident, automated accusation against everyone else's repository.

**If two reputable sources disagree, do not pick one.** Add the gas, exclude the disputed report in `exclusions`, and write the reason. SF₆ AR6 is the worked example: GHG Protocol says 24,300, IPCC says 25,200, and the tool refuses to judge it rather than taking a side.

## What will not be merged

- **Proximity matching** — inferring a report from a nearby mention rather than a column header. It has been tried and it flags correct prose while missing wrong cells. See [#1](https://github.com/greencalculus/gwp-basis-check/issues/1), which wants the coverage without the technique.
- **Reporting a value as stale.** This tool does not have an opinion on which report you should use. AR4 and AR5 values are frequently correct by law.
- **Treating NOT CHECKED as clean.** They are different answers and the distinction is deliberate.

## Before you open a PR

```bash
python3 gwp_basis_check.py --self-test    # 9 cases + reference integrity
python3 render_tables.py --check          # README tables match the reference
python3 gwp_basis_check.py README.md      # the tool passes its own docs
```

CI runs all three on Python 3.9, 3.11 and 3.13, plus a check that adding a report is still a data-only change. If you changed `gwp_reference.json`, run `python3 render_tables.py` and commit the README too.

## Commit messages

Say what changed and why it was wrong before. The subject is a sentence, not a label.

## Questions

Open an issue, or comment on the one you want to work on — including to say you are stuck. That is the normal question, not a silly one.

Security issues go to **security@greencalculus.com**, not to an issue.
