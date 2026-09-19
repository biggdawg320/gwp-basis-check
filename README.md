# gwp-basis-check

Finds greenhouse-gas warming-potential tables that contradict the IPCC assessment report they name.

```
$ gwp_basis_check.py factors/gwp.py

=== factors/gwp.py  (26 labelled gas records) ===
  MISLABEL    r-410a   field 'ar5' = 2088  -> that is AR4's value; AR5 published 1923
```

## The problem

Every greenhouse gas gets a multiplier saying how much warming it causes relative to CO₂. Those multipliers are revised with each IPCC assessment report: HFC-134a is **1,430** in AR4 (2007), **1,300** in AR5 (2013) and **1,530** in AR6 (2021).

So a multiplier alone is meaningless. `1430` is a perfectly correct number — under AR4. It becomes a defect only when the code calls it AR5.

**This tool does not tell you your numbers are out of date.** Old values are usually correct: the EU F-Gas Regulation mandates AR4, EU ETS moved to AR5 in the 2023 amendment, and DEFRA and UNFCCC reporting use AR5. Telling those projects they are stale would be wrong, and wrong most of the time.

It checks one thing: **does the value match the report the file itself names?**

## Two tests

| | |
|---|---|
| `MISLABEL` | a field named `ar5` holding the number AR4 published for that gas |
| `COLUMN_COPY` | every row's `ar6` equal to its `ar5`, in a file naming both |

Blends are where this usually bites. A blend's GWP is the mass-weighted average of its components, so it is **re-derived at every assessment report** — R-410A is 2,088 under AR4 and 2,256 under AR6. It is widely believed that blend values carry across unchanged. They do not, and one AR-agnostic figure ends up in every column. In the wild the pure compounds are typically all correct and only the blends are wrong, which is exactly why nobody notices.

## Why it does not go stale

The tests rest only on what the reports published, and **AR4, AR5 and AR6 are closed**. Their numbers will not change again. A check built on them stays valid without maintenance, and never has to argue that its own value is the right one — it reports only that a file disagrees with the report it cites.

## Install and run

No dependencies, Python 3.9+.

```bash
curl -O https://raw.githubusercontent.com/greencalculus/gwp-basis-check/main/gwp_basis_check.py
curl -O https://raw.githubusercontent.com/greencalculus/gwp-basis-check/main/gwp_reference.json

python3 gwp_basis_check.py src/**/*.py            # or .ts .js .json .md .html .csv
python3 gwp_basis_check.py --json factors.py      # machine-readable
python3 gwp_basis_check.py --self-test
```

Exit codes: `0` nothing found · `1` findings · `2` nothing was checkable.

## What it reads

- a record carrying a gas name plus `ar4`/`ar5`/`ar6` fields (JSON, TS, Python, SQL seed rows)
- one map per report, keyed by gas — `GWP_AR5 = {"R410A": 1924, ...}`
- HTML, markdown and CSV tables **whose column header names a report**

Tables are read by mapping the header and then reading down the column. Proximity scanning is deliberately not used: a comparison page legitimately puts AR4, AR5 and AR6 numbers within a few characters of each other, and a window scan produces confident nonsense.

## "NOT CHECKED" is not "clean"

If no gas table in a readable shape is found, the tool says **NOT CHECKED** and exits 2. A checker that understood nothing and reported green is worse than one that reports red, because it retires the question. Absence of a finding there is absence of a reading.

## What it deliberately will not judge

Encoded in `gwp_reference.json` with a written reason for each:

| | |
|---|---|
| **SF₆ AR6** | Sources disagree on what AR6 published — GHG Protocol v2.0 prints 24,300, IPCC AR6 Table 7.SM.7 gives 25,200. Neither can be called "the label's value". |
| **CH₄ fossil AR5** | A convention, not a value. AR5 Table 8.7 publishes a single 28 regardless of origin; GHG Protocol applies a +2 oxidation adjustment to reach 30. DEFRA and UNFCCC use 28. |
| **HFO-1234yf AR5** | AR5 published `<1` — a bound, not a number you can compare. |
| **Unqualified CH₄** | AR6 publishes 27.0 non-fossil, 29.8 fossil and 27.9 origin-agnostic. A bare methane row cannot be judged. |
| **HCFC-22** | No row in the reference, so the tool is blind to it. Published: AR4 1,810 / AR5 1,760 / AR6 1,960. |
| **SAR columns** | Out of scope. SAR and AR5 both give HFC-134a 1,300. |

Two of those exist because **GreenCalculus holds the contested position**. When a naive version of this tool was pointed at a US national laboratory's tooling, two of its three complaints were exactly these. Neither was the lab's error.

## Limits, stated plainly

- **Precision is bought with recall.** A wrong number that matches no other report's value is not reported, because it cannot be *proven* mislabelled. Real errors are missed on purpose.
- **Coverage is the binding constraint.** In a scan of 1,071 files drawn from GitHub code search, only 17 were in a readable shape. Most files mentioning an assessment report are imports, prose or scenario names.
- **Tables whose report is named in a section heading rather than a column header are not read.** See the open issues — this is wanted, but it has to be built without reintroducing proximity matching.

## Where the numbers come from

`gwp_reference.json` — 44 gases, pulled from the [GreenCalculus](https://greencalculus.com) keyless API and reconciled against *GHG Protocol, "Global Warming Potential Values", v2.0, August 2024*. The regeneration command is in the file.

**Adding AR7 later is a data change, not a code change.** Append it to `bases`, add its values, and the field patterns, header matcher and comparison order all widen on their own. CI asserts this.

## Provenance, and why you should not take our word for it

GreenCalculus sells emission-factor data, so treat a tool from us with appropriate suspicion — which is why the method, the reference values and every exclusion are here to be argued with.

**The same method was first run against our own corpus. It found 66 wrong cells out of 407 checked**, including AR4 blend values printed under an AR6 heading on our single most-visited page. The root cause was the blend-invariance belief described above. That is what this tool was built to catch, and we were not the exception to it.

## Contributing

See the open issues. The self-test is the safety net: nine cases, of which **six are negatives** — a correct three-report table, an EU F-Gas table (AR4 by law), the two contested figures, CO₂, HFC-507A and bare CH₄. A change that makes any of those fire is a change that sends a correction to someone who was right. CI runs them on Python 3.9, 3.11 and 3.13, and also asserts that adding a report stays a data-only change.

MIT.
