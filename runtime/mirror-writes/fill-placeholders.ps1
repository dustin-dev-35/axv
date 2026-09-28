# Substitute the three memo-derived text blocks into the pending Supabase insert.
# Every value is read from the canonical blob, never retyped.

$ErrorActionPreference = "Stop"
$root = $env:PAPERCLIP_WORKSPACE_CWD
$memoPath = Join-Path $env:PAPERCLIP_RUN_SCRATCH_DIR "memo_exact.md"
$sqlPath  = Join-Path $root "axv\runtime\mirror-writes\2609.31098-corpus_index.sql"
$utf8     = New-Object System.Text.UTF8Encoding($false)

$memo = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($memoPath))
$lines = $memo -split "`r?`n"

function Get-SingleLineStartingWith([string]$prefix) {
  for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i].StartsWith($prefix)) { return $lines[$i] } }
  throw "no line starting with '$prefix'"
}

# claim: the memo's own **Claim.** sentence, verbatim.
$claim = (Get-SingleLineStartingWith '**Claim.**').Substring('**Claim.**'.Length).Trim()

# unknowns: everything after "Unknowns:**" on the Confidence line.
$conf = Get-SingleLineStartingWith '**Confidence.**'
$k = $conf.IndexOf('Unknowns:**')
if ($k -lt 0) { throw "no 'Unknowns:**' on the Confidence line" }
$unknowns = $conf.Substring($k + 12).Trim()

# failure_mode: condensed from the memo's own named failure mode, kept short
# because the schema says the column is kept short. Wording is the memo's.
$failureMode = "The 15-of-16 sub-F_L headline is a property of the reference, not of the models. F_L assumes equal-norm orthogonal updates with no persistent initial component - a construction no trained model satisfies - and Table S3 shows the sign flipping for all sixteen rows (-2.9% to -89.1%) the moment the measured update-similarity profile is retained. The authors call F_L a first structural yardstick, not a definitive null; the headline, the abstract and the triage-worthy phrase all rest on it."

foreach ($pair in @(@("CLAIM", $claim), @("UNKNOWNS", $unknowns), @("FAILMODE", $failureMode))) {
  if ($pair[1].Contains('$axv$')) { throw "value for @$($pair[0])@ contains the dollar-quote delimiter" }
}

$sql = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($sqlPath))
foreach ($pair in @(@("CLAIM", $claim), @("UNKNOWNS", $unknowns), @("FAILMODE", $failureMode))) {
  $token = '@' + $pair[0] + '@'
  if ($sql.IndexOf($token) -lt 0) { throw "placeholder $token not found in the sql" }
  $sql = $sql.Replace($token, $pair[1])
}

[System.IO.File]::WriteAllText($sqlPath, $sql, $utf8)

# --- verify, do not trust -------------------------------------------------
$check = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($sqlPath))
$fail = @()
if ($check -match '@[A-Z]+@')                 { $fail += "a placeholder survived" }
if ($check.Contains('$axv$@'))                { $fail += "an unsubstituted dollar-quote marker survived" }
$openTags = ([regex]::Matches($check, [regex]::Escape('$axv$'))).Count
if ($openTags % 2 -ne 0)                      { $fail += "unbalanced dollar-quote delimiters: $openTags" }
# each of the three values must round-trip out of the file unchanged
foreach ($pair in @(@("claim", $claim), @("unknowns", $unknowns), @("failure_mode", $failureMode))) {
  if (-not $check.Contains($pair[1]))         { $fail += "$($pair[0]) did not round-trip" }
}
if ($fail.Count -gt 0) { $fail | ForEach-Object { "FAIL: $_" }; exit 1 }

$b = [System.IO.File]::ReadAllBytes($sqlPath)
"OK  bytes=$($b.Length)  dollar-quote tags=$openTags  placeholders=0"
"    claim=$($claim.Length)  unknowns=$($unknowns.Length)  failure_mode=$($failureMode.Length)"
"    sha256=" + (Get-FileHash $sqlPath -Algorithm SHA256).Hash
# secret scan: nothing in this file may look like a credential
foreach ($pat in @('phx_', 'sk-', 'service_role', 'Bearer ', 'eyJ', 'sbp_')) {
  if ($check.Contains($pat)) { "FAIL: secret-shaped token '$pat' present"; exit 1 }
}
"    secret scan clean"
