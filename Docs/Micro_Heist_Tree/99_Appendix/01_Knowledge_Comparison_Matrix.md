# Knowledge Comparison Matrix

## Purpose
- Compare key rules between local (authoritative) sources and trusted supporting sources.
- Local wins on conflict; trusted sources provide rationale only (no numeric thresholds).
- Verification order MUST NOT be swapped: (1) Online trusted books, (2) Online trusted sources, (3) AI Database, (4) Project Docs -> then compare; if conflict, use the stricter/safer local interpretation.
- If local is ambiguous, mark [INBOX-REVIEW] and default to stricter gating.

## Matrix
| ID | Concept / Rule | Local Source (authoritative) | Trusted Source (supporting) | What we take from trusted source | Conflict' | Final Decision | Notes / [INBOX-REVIEW] |
|---:|---|---|---|---|---|---|---|
| CM-01 | Reduce/Exit invariant | 01_Foundations/04_Core_Invariants.md | TS-01 (O'Hara 1995) | Terminology clarity on reduce/exit and inventory-risk bias | No | KEEP | - |
| CM-02 | Confirmed flip + mandatory exit | 03_Bias_System/03_Bias_Degrade_vs_Flip.md | TS-06 (Hamilton 1989); TS-07 (Ang 2011) | Rationale for persistence/hysteresis in regime shifts; avoid flip-flop | No | KEEP | [INBOX-REVIEW] if local flip persistence needs more detail |
| CM-03 | Readiness blocks entries, exits allowed | 08_Operational_Robustness/01_Readiness_and_Health_Gates.md | TS-02 (Hasbrouck 2007) | Why degraded quality/latency/microstructure risk justifies blocking entries | No | KEEP | - |
| CM-04 | Regime taxonomy (6 regimes) | 04_Regimes_and_Routing/01_Regime_Taxonomy.md | TS-05 (Cont 2001); TS-06; TS-07; TS-04 (Brunnermeier & Pedersen 2009) | Justify volatility clustering, regime persistence, and shock/liquidity fragility framing | No | KEEP | Keep 6 regimes; explicitly include shock override + confidence/unknown routing (no new numeric thresholds). (Advisory: TS-05, TS-06, TS-07, TS-04) |
| CM-05 | Unknown-mode behavior | 04_Regimes_and_Routing/03_Unknown_Mode.md | TS-05; TS-06; TS-07 | Clarify "when uncertain, tighten-only"; hysteresis/persistence before re-entry | No | KEEP | Hysteresis+persistence; TF conflict/low confidence => Unknown-Mode; router-eligibility blocks entries (tighten-only). (Advisory: TS-05, TS-06, TS-07) |
| CM-06 | Edge-positive gate | 05_Setups/05_Confirmation_Gates.md | TS-02 (Hasbrouck 2007); TS-03 (Almgren & Chriss 2000) | Edge must exceed costs/impact; cost components rationale | No | KEEP | Define cost components conceptually; no numbers added. |
| CM-07 | Adaptive Parameters Policy | 04_Regimes_and_Routing/04_Adaptive_Parameters_Policy.md | TS-07 (Ang 2011); TS-06 (Hamilton 1989) | Tighten-only, anti-drift, and stability before adapting | No | KEEP | Define allowed adaptive list explicitly; default to strict under uncertainty. |

## Trusted Sources (minimal bibliography)
- TS-01: Maureen O'Hara - "Market Microstructure Theory" (1995).
- TS-02: Joel Hasbrouck - "Empirical Market Microstructure" (2007).
- TS-03: Robert Almgren & Neil Chriss - "Optimal Execution of Portfolio Transactions" (2000).
- TS-04: Markus Brunnermeier & Lasse Pedersen - "Market Liquidity and Funding Liquidity" (2009).
- TS-05: Rama Cont - "Empirical properties of asset returns: stylized facts and statistical issues" (2001).
- TS-06: James D. Hamilton - "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle" (1989).
- TS-07: Andrew Ang - "Regime Changes and Financial Markets" (2011, NBER WP).

## Conflict Resolution Checklist
1) Restate the local rule (as invariant/adaptive/override).  
2) Restate the trusted-source claim.  
3) Identify the conflict (scope, definition, threshold, behavior).  
4) Apply the rule: Local wins.  
5) If local is ambiguous: mark [INBOX-REVIEW] and default to stricter gating.  
