$ErrorActionPreference = "Stop"
trap {
  Write-Host "`nERROR:`n$($_ | Out-String)" -ForegroundColor Red
  Read-Host "Press Enter to close"
  break
}

# === REPO ROOT HEADER (MANDATORY) ===
$RepoRoot = "E:\studycase1"
if (-not (Test-Path $RepoRoot)) { throw "RepoRoot not found: $RepoRoot" }
Set-Location $RepoRoot

$top = (git rev-parse --show-toplevel).Trim()

function NormalizePath([string]$p) {
  if ([string]::IsNullOrWhiteSpace($p)) { return "" }
  return (($p -replace '/', '\').TrimEnd('\'))
}

if ((NormalizePath $top) -ne (NormalizePath $RepoRoot)) {
  throw "Wrong repo root. Expected '$RepoRoot' but got '$top'."
}

# Hard stop if dirty (no passing)
$dirty = git status --porcelain
if ($dirty.Count -gt 0) {
  Write-Host "Working tree is not clean. Modified/untracked files:" -ForegroundColor Yellow
  $dirty | ForEach-Object { Write-Host $_ }
  throw "Working tree is not clean. Commit/stash changes before running."
}

# Detect base branch from origin/HEAD; fallback "main"
$originUrl = (git remote get-url origin).Trim()
if (-not $originUrl) { throw "Remote 'origin' not found or has no URL." }

$BASE_BRANCH = "main"
try {
  $headRef = (git symbolic-ref refs/remotes/origin/HEAD).Trim()
  if ($headRef -match "refs/remotes/origin/(.+)$") { $BASE_BRANCH = $Matches[1] }
} catch {}

git checkout $BASE_BRANCH | Out-Host
git pull --ff-only origin $BASE_BRANCH | Out-Host

# =======================
# HARD PATHS (NO PASSING)
# =======================
$UnknownPath = Join-Path $RepoRoot "Docs\Micro_Heist_Tree\04_Regimes_and_Routing\03_Unknown_Mode.md"
$MenuPath    = Join-Path $RepoRoot "Docs\Micro_Heist_Tree\05_Setups\01_Setup_Menu.md"
$MomPath     = Join-Path $RepoRoot "Docs\Micro_Heist_Tree\05_Setups\03_Momentum_Setups.md"

foreach ($p in @($UnknownPath, $MenuPath, $MomPath)) {
  if ([string]::IsNullOrWhiteSpace($p)) { throw "Computed path is empty. This must never happen." }
  if (-not (Test-Path $p)) { throw "Target file missing at exact path: $p" }
}

# =======================
# UTF-8 IO (PS 5.1 safe)
# =======================
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function ReadText([string]$path) {
  if ([string]::IsNullOrWhiteSpace($path)) { throw "ReadText: path is empty." }
  if (-not (Test-Path $path)) { throw "ReadText: file not found: $path" }
  return [System.IO.File]::ReadAllText($path, $Utf8NoBom)
}

function WriteText([string]$path, [string]$content) {
  if ([string]::IsNullOrWhiteSpace($path)) { throw "WriteText: path is empty." }
  $dir = Split-Path -Path $path -Parent
  if ([string]::IsNullOrWhiteSpace($dir)) { throw "WriteText: parent dir is empty for path: $path" }
  if (-not (Test-Path $dir)) { throw "WriteText: parent dir missing (should already exist): $dir" }
  [System.IO.File]::WriteAllText($path, $content, $Utf8NoBom)
}

function EnsureNewline([string]$s) {
  $s = ($s + "")
  if ($s -notmatch "(\r\n|\n)\z") { return $s + "`r`n" }
  return $s
}

# ========= 1) Unknown-mode canonical strict throttle plan =========
$unknown = ReadText $UnknownPath
$unknownMarker = "## Canonical Unknown-Mode Strict Throttle Plan (if enabled)"

if ($unknown -notmatch [regex]::Escape($unknownMarker)) {
  $insert = @"
$unknownMarker

**Default is still BLOCK.** THROTTLE is a **rare exception** and must never be used to 'find trades'.

### Allowed pattern (only)
- **MO-2: Breakout + Retest + Go** (only after a **confirmed hold**; no mid-retest guessing).

### Gates (MUST all hold)
- **Eligibility stays absolute**: Readiness/Health PASS, Data Quality OK, Micro Sanity PASS.
- **No Shock/Dislocation**: any fragility symptoms -> escalate to AVOID/BLOCK.
- **Bias alignment required**: if `bias_conflict_flag=TRUE` -> BLOCK.
- **Readable structure**:
  - One clean level (no multi-level chop).
  - Retest hold is unambiguous (closed-bar + persistence).
- **Confirmations are stricter than normal** (never looser):
  - Closed-bar hold + persistence required.
  - No 'early' entries inside the retest.
- **Edge-positive remains required**: if edge vs friction is unclear -> BLOCK.

### Frequency + failure handling (tighten-only)
- THROTTLE means **fewer attempts** + **higher selectivity** (do not 'cycle' attempts).
- After **any failed attempt**, enforce cooldown (no immediate re-attempt).
- If repeated failures begin to appear -> revert Unknown-mode to **BLOCK** (no bargaining).
- Exits are always allowed; management remains **reduce-first**.

### Cooldown reference (MUST)
- See: `Docs/Micro_Heist_Tree/06_Risk_and_Frequency/04_Cooldowns_and_NoTrade.md`
"@

  $strictHdr = '(?m)^\s*##\s+Strict Throttle Exception\s*$'
  if ([regex]::IsMatch($unknown, $strictHdr)) {
    $rx = New-Object System.Text.RegularExpressions.Regex($strictHdr, [System.Text.RegularExpressions.RegexOptions]::Multiline)
    $unknown = $rx.Replace($unknown, { param($m) ($m.Value + "`r`n`r`n" + $insert) }, 1)
    $unknown = EnsureNewline $unknown
  } else {
    $unknown = ($unknown.TrimEnd() + "`r`n`r`n" + $insert + "`r`n")
  }

  WriteText $UnknownPath $unknown
  Write-Host "[OK] Updated Unknown-mode: $UnknownPath"
} else {
  Write-Host "[SKIP] Unknown-mode section already present."
}

# ========= 2) Setup Menu tie-break =========
$menu = ReadText $MenuPath
$menuMarker = "## Tie-break: TREND vs BREAKOUT (when both appear eligible)"

if ($menu -notmatch [regex]::Escape($menuMarker)) {
  $tieBreak = @"
$menuMarker

Apply this ladder **in order**:

1) **Route-mode wins.** If Router outputs a single `route_mode` (TREND or BREAKOUT), pick that family (do not mix).
2) If Router allows both families (ambiguity remains), choose **the clearer structure**:
   - Choose **BREAKOUT** if a clean level exists and the breakout has a **confirmed retest hold** (MO-2 shape).
   - Choose **TREND** if an orderly pullback exists and continuation structure confirms (MO-3 shape) without level-chop.
3) If neither structure is clearly dominant -> default stricter: `entry_policy=THROTTLE` or `BLOCK` (prefer BLOCK if uncertainty remains).
"@

  $menu = $menu.TrimEnd() + "`r`n`r`n" + $tieBreak + "`r`n"
  WriteText $MenuPath $menu
  Write-Host "[OK] Updated Setup Menu: $MenuPath"
} else {
  Write-Host "[SKIP] Setup Menu tie-break already present."
}

# ========= 3) Momentum references =========
$mom = ReadText $MomPath

$refBlock = @"
## References (resolves prior open questions)

- **Unknown-mode strict throttle plan (canonical):**
  - `Docs/Micro_Heist_Tree/04_Regimes_and_Routing/03_Unknown_Mode.md` -> 'Canonical Unknown-Mode Strict Throttle Plan (if enabled)'
- **TREND vs BREAKOUT tie-break (deterministic):**
  - `Docs/Micro_Heist_Tree/05_Setups/01_Setup_Menu.md` -> 'Tie-break: TREND vs BREAKOUT (when both appear eligible)'
"@

$openPattern = '(?ms)^\s*##\s+Open Questions\s*$.*?(?=^\s*##\s+|\z)'
$rxOpen = New-Object System.Text.RegularExpressions.Regex(
  $openPattern,
  ([System.Text.RegularExpressions.RegexOptions]::Multiline -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
)

if ($rxOpen.IsMatch($mom)) {
  $mom = $rxOpen.Replace($mom, ($refBlock + "`r`n"), 1)
  $mom = EnsureNewline $mom
  WriteText $MomPath $mom
  Write-Host "[OK] Replaced Open Questions in Momentum: $MomPath"
} elseif ($mom -match '\[INBOX-REVIEW\]') {
  $mom = $mom.TrimEnd() + "`r`n`r`n" + $refBlock + "`r`n"
  WriteText $MomPath $mom
  Write-Host "[OK] Appended References to Momentum: $MomPath"
} else {
  Write-Host "[SKIP] Momentum has no Open Questions and no INBOX-REVIEW markers."
}

# ========= COMMIT + PUSH =========
if ((git status --porcelain).Count -eq 0) {
  Write-Host "No changes detected. Nothing to commit."
  Read-Host "Done. Press Enter to close"
  exit 0
}

git add -A | Out-Host
git commit -m "chore(setups): canonize Unknown throttle + trend/breakout tie-break" | Out-Host
git push origin $BASE_BRANCH | Out-Host

$sha = (git rev-parse HEAD).Trim()
if ($originUrl -match "^https://github\.com/([^/]+)/([^/]+?)(\.git)?$") {
  $owner = $Matches[1]; $repo = $Matches[2]
  $commitUrl = "https://github.com/$owner/$repo/commit/$sha"
  Write-Host "Commit: $commitUrl"
  Set-Clipboard -Value $commitUrl
} else {
  Write-Host "Commit SHA: $sha"
  Set-Clipboard -Value $sha
}

git show --name-status --shortstat --oneline HEAD | Out-Host
Read-Host "Done. Press Enter to close"
