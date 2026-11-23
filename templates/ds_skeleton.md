<!--
  DS SKELETON — copy to the output folder and fill in.
  Delete these comment blocks before generating the deliverable.
  Placeholders are written {LIKE_THIS}. Any placeholder left in the final
  document fails the artifact scan.
-->

![Dominion Dynamics](assets/dominion_dynamics_logo.jpg){width=60mm}

<!-- Cover logo. The default is the Dominion Dynamics mark shipped in the
     skill's assets/ folder. If the house DOCX template already carries the
     logo in its header or cover, delete this line so it is not shown twice. -->

# {BLOCK_NAME} — Hardware Design Specification

**Document number:** {DOC_NUMBER}  
**Official revision:** {OFFICIAL_REV}  
**Status:** {STATUS}  <!-- Draft or Released; ask the user before changing -->  
**Author(s):** {AUTHORS}  
**Build:** {CURRENT_BUILD}  

## Abstract

<!-- 3–6 sentences: what the block does, its envelope, its key risks, and the
     status of the open items that gate schematic freeze. -->

## Revisions

| Revision | Date | Description | Author |
|---|---|---|---|
| {OFFICIAL_REV} | {DATE_OR_DRAFT} | {DESCRIPTION} | {AUTHOR} |

## Acknowledgments and legal

<!-- House text, if any. Otherwise: "Not applicable — internal design document." -->

## Draft Working History

> This internal working history is not part of the official document revision.
> Official document revision remains {OFFICIAL_REV}.

| Pass | Date | Scope of change | Tool / author |
|---|---|---|---|
| D-01 | {DATE_OR_DRAFT} | Initial draft from {SOURCES} | {TOOL} |

## Table of Contents

<!-- Leave this heading in place with nothing under it. scripts/build_docx.py
     inserts a Word TOC field here at build time (and styles this and the other
     front-matter headings so the TOC does not list them or the cover). For a
     Markdown-only deliverable, either delete this heading or replace it with a
     list of links to the body sections; do not leave an empty heading. -->

---

## 1. Introduction and Scope

### 1.1 Purpose
<!-- What this block is for and who uses this document. -->

### 1.2 Scope
- In scope: {IN_SCOPE}
- Out of scope: {OUT_OF_SCOPE}

### 1.3 DS, EVS and EVR
This document states design intent and derivations. Verification is defined in the EVS {EVS_REF}. Measured results belong in the EVR {EVR_REF}. No measured results appear here.

## 2. System Context and Block Diagram

<!-- Where the block sits in the system. One block diagram naming every interface. -->

**Figure 2-1.** {BLOCK_DIAGRAM_CAPTION}

## 3. Requirements and Operating Envelope

**Table 3-1.** Requirements

| ID | Parameter | Requirement | Min | Nom | Max | Unit | Source (doc, rev, approval state) | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| REQ-01 | {PARAM} | {REQUIREMENT} | | | | {UNIT} | {SOURCE} | Confirmed | |

<!-- A row with no Source is not a requirement. Mark it Open Item instead. -->

## 4. External Interfaces

**Table 4-1.** External interfaces (relevant to this block only)

| Signal / pin | Direction | Type / level | Min | Max | Connector / ref | Status | Notes |
|---|---|---|---|---|---|---|---|

## 5. Internal Interfaces

**Table 5-1.** Internal interfaces

| Signal | Device pin (datasheet) | Function | Level | Status | Notes |
|---|---|---|---|---|---|

<!-- Pin numbers and names verified against the datasheet. Per-row status for anything unconfirmed. -->

## 6. Design Description

### 6.1 Topology and operating modes
### 6.2 Control scheme
### 6.3 Protection features

## 7. Component Selection Rationale

**Table 7-1.** Critical components

| Ref | Part / value | Key ratings | Derated to | Selection reason | Alternates | Status |
|---|---|---|---|---|---|---|

## 8. Calculations

<!-- One sub-section per applicable item in calculation_checklists.md. For each:
     equation, inputs (with source), result, status. Mark not-applicable items. -->

### 8.1 {CALCULATION_NAME}

**Equation:** 
**Inputs:** 
**Result:** 
**Status:** 

## 9. Derating and Margin Analysis

**Table 9-1.** Derating

| Part / node | Parameter | Actual (worst case) | Rated | Derating target | Margin | Status |
|---|---|---|---|---|---|---|

<!-- State the margin rule used, and quantify every marginal area. -->

## 10. Start-up, Shut-down and Sequencing

**Table 10-1.** Event sequence

| Step | Event | Threshold / timing | Behaviour on fault | Status |
|---|---|---|---|---|

## 11. Budget (power, signal or timing)

**Table 11-1.** Budget roll-up

| Stage / branch | Input | Output | Assumed efficiency / margin | Status |
|---|---|---|---|---|

## 12. Implementation, Schematic and BOM Reconciliation

**Table 12-1.** Mismatches

| Item | Schematic | BOM | Datasheet / reference | Chosen value and source | Action | Owner |
|---|---|---|---|---|---|---|

## 13. Risks and Marginal Areas

**Table 13-1.** Risk register — see `templates/risk_register_table.md` for the format.

## 14. Open Items and Review Questions

**Table 14-1.** Open items — see `templates/open_items_table.md` for the format.

## 15. Future-Spin Recommendations

<!-- Changes for the next build only. Not current-build actions. -->

## 16. Appendix and Acronyms

| Acronym | Meaning |
|---|---|

## 17. Reference Documents

| Ref | Document | Number | Revision | Date |
|---|---|---|---|---|
