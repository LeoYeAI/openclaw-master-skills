# ERC-3643 Compliance Assessment

## Overview

Performs structured ERC-3643 (T-REX Protocol) compliance assessments for security token projects. Use when a user asks about token compliance, ONCHAINID verification, transfer restriction architecture, investor eligibility, or regulatory readiness for RWA tokenization.

## When to Use

- User mentions ERC-3643, T-REX, security tokens, or RWA (Real World Asset) tokenization
- User asks about investor eligibility, KYC/AML claim verification, or ONCHAINID
- User needs a compliance gap analysis before SEBI, MiCA, VARA, SEC, or FSCA token registration
- User asks whether their token architecture supports institutional transfer restrictions
- User is building on Tokeny, ONCHAINID, or T-REX-compatible stacks

## Capabilities

### 1. Compliance Gap Analysis
Assesses a token project against the 6 ERC-3643 compliance pillars:
- Identity Management (ONCHAINID/ERC-734/ERC-735 claim structure)
- Compliance Module (transfer restriction logic: MaxBalance, CountryRestrict, etc.)
- Token Permissions (forced transfers, recovery, freezing)
- Investor Registry (identity registry linkage and country controls)
- Agent Architecture (TREX factory roles and access control)
- Regulatory Jurisdiction Mapping (MiCA/VARA/SEC/SEBI applicability)

### 2. Transfer Restriction Audit
Reviews the T-REX compliance module configuration:
- Active compliance modules and their parameters
- canTransfer() path and failure modes
- Whitelist architecture and investor onboarding flow

### 3. Cross-Standard Conflict Detection
Identifies conflicts when ERC-3643 is combined with:
- ERC-7518 (DyCIST dynamic compliance)
- ERC-4626 (tokenized vault standards)
- ERC-1404 (Simple Restricted Token Standard)
- ERC-4337 (Account Abstraction wallet interactions)

### 4. Regulatory Readiness Report
Produces a structured gap report with:
- Jurisdiction-specific requirements (MiCA Art. 68, VARA STO Framework, SEBI AIF/REIT)
- Pass/Fail/Partial status for each pillar
- Prioritized remediation roadmap
- Estimated effort per gap

## Usage Examples

**Basic assessment:**
Assess the ERC-3643 compliance posture of [project name].
Focus on transfer restriction architecture and ONCHAINID claim structure.

**Gap analysis for token launch:**
We're preparing a security token for SEBI registration.
Run an ERC-3643 gap analysis focused on investor eligibility verification and compliance module configuration.

**Cross-standard conflict check:**
Our token uses both ERC-3643 and ERC-7518 for dynamic compliance.
Check for identity claim conflicts between the two standards.

**Regulatory readiness:**
Produce an ERC-3643 compliance readiness report for MiCA Title IV (ART/EMT framework).

## Output Format

Returns a structured compliance report:

ERC-3643 COMPLIANCE ASSESSMENT
Project: [name] | Standard: ERC-3643 T-REX v4 | Jurisdiction: [MiCA/VARA/SEBI/SEC/FSCA]

PILLAR SCORES
- Identity Management:  PASS / PARTIAL / FAIL
- Compliance Module:    ...
- Token Permissions:    ...
- Investor Registry:    ...
- Agent Architecture:   ...
- Regulatory Mapping:   ...

OVERALL SCORE: [X/6 pass] | RISK: [Low/Medium/High/Critical]

FINDINGS: [title] - [severity] / Issue / Recommendation / Effort

REMEDIATION ROADMAP: P1 Critical / P2 High / P3 Medium

## Context Notes

- ERC-3643 is the leading security token standard (deployed by Tokeny, RealT, Securitize, Mt Pelerin)
- T-REX Protocol: Token + IdentityRegistry + IdentityRegistryStorage + TrustedIssuersRegistry + ClaimTopicsRegistry + Compliance
- ONCHAINID (ERC-734/ERC-735) provides identity primitive; claims issued by trusted ClaimIssuers
- Transfer restrictions enforced on-chain via modular Compliance contracts (not off-chain)
- Related: ERC-1404 (simpler), ERC-7518 (dynamic), ERC-1400 (partition-based)

## Author

Fuseini Mohammed - ERC-3643 Compliance Consultant
GitHub: fuseinimetadata-commits | nexus-hedera: AI compliance agent with live Hedera testnet verification
