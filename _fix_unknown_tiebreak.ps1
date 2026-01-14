$top = (git rev-parse --show-toplevel).Trim()

function NormalizePath([string]$p) {
  if ([string]::IsNullOrWhiteSpace($p)) { return "" }
  return (($p -replace '/', '\').TrimEnd('\'))
}

if ((NormalizePath $top) -ne (NormalizePath $RepoRoot)) {
  throw "Wrong repo root. Expected '$RepoRoot' but got '$top'."
}
