# Validate the pending corpus_index insert against the DDL it will run against.
# Nothing here trusts a prior run's summary. The DDL is read from the installed
# storage-contract skill; the insert is read from the working tree.
$ErrorActionPreference = "Stop"
$ddlPath = "C:\Users\dusti\.paperclip\instances\default\companies\5064e629-761a-4ec9-9c64-97ec4f1c17fb\agents\1dc764c3-1c49-4bca-98de-571538e391a5\instructions/../../../skills/5064e629-761a-4ec9-9c64-97ec4f1c17fb/storage-contract/scripts/schema.sql"
if (-not (Test-Path -LiteralPath $ddlPath)) {
  $ddlPath = "C:\Users\dusti\.claude\skills\storage-contract--f81af11d62\scripts\schema.sql"
}
if (-not (Test-Path -LiteralPath $ddlPath)) { throw "schema.sql not found in either location" }
$sqlPath = "$env:PAPERCLIP_WORKSPACE_CWD\axv\runtime\mirror-writes\2609.31098-corpus_index.sql"
"ddl : $ddlPath"
"ins : $sqlPath"

$ddl  = [System.IO.File]::ReadAllText($ddlPath, [System.Text.Encoding]::UTF8)
$ins  = [System.IO.File]::ReadAllText($sqlPath,  [System.Text.Encoding]::UTF8)
$fail = @()

# --- 1. parse the DDL for a table -------------------------------------------
function Get-Table([string]$text, [string]$table) {
  $m = [regex]::Match($text, "create table if not exists $table \((?<body>.*?)\n\);", 'Singleline')
  if (-not $m.Success) { throw "table $table not found in the DDL" }
  return $m.Groups['body'].Value
}
function Get-Columns([string]$body) {
  $cols = @{}
  foreach ($line in ($body -split "`r?`n")) {
    $t = $line.Trim()
    if ($t -eq '' -or $t -match '^(create|unique|primary|foreign|check|constraint)\b') { continue }
    $m = [regex]::Match($t, '^(?<n>[a-z_]+)\s+(?<ty>[a-z]+(?:\s*\([^)]*\))?)')
    if (-not $m.Success) { continue }
    $cols[$m.Groups['n'].Value] = @{
      type      = $m.Groups['ty'].Value
      notnull   = ($t -match 'not null')
      hasdefault = ($t -match 'default ')
    }
  }
  return $cols
}

foreach ($t in @('corpus_index','mirror_health')) {
  $cols = Get-Columns (Get-Table $ddl $t)
  $body = Get-Table $ddl $t
  "--- $t : $($cols.Count) columns"

  # Extract the column list and the values block with a scanner rather than a regex.
  # The values contain parentheses inside dollar-quoted memo text and inside SQL
  # comments, so a non-greedy regex truncates the block and the count it produces is
  # wrong - a validator that is wrong in the safe direction is worse than none.
  #
  # A dollar-quoted literal is one atomic unit. Read the opening delimiter as
  # `$` + tag + `$`, then find that same delimiter again and skip past it.
  # Two earlier versions of this were wrong in the same way and it is worth
  # recording why: skipping only to the *next* `$` lands inside the literal and
  # scans its text as SQL, and tracking the tag in a state machine mis-closes on
  # the *next* literal's opening delimiter. A string search for the full closing
  # delimiter is the version that is actually right.
  function Skip-Quoted([string]$text, [int]$i) {
    $tagEnd = $text.IndexOf('$', $i + 1)
    if ($tagEnd -lt 0) { throw "unterminated dollar-quote tag at offset $i" }
    $tag = $text.Substring($i + 1, $tagEnd - $i - 1)
    $close = $text.IndexOf('$' + $tag + '$', $i + 1)
    if ($close -lt 0) { throw "unterminated dollar-quoted literal with tag '$tag' at offset $i" }
    return ($close + $tag.Length + 2)
  }
  function Find-Balanced([string]$text, [int]$openIdx) {
    $depth = 0; $i = $openIdx
    while ($i -lt $text.Length) {
      $ch = $text[$i]
      if ($ch -eq '$') { $i = Skip-Quoted $text $i; continue }
      if ($ch -eq '(') { $depth++ }
      elseif ($ch -eq ')') { $depth--; if ($depth -eq 0) { return $i } }
      $i++
    }
    throw "unbalanced paren from offset $openIdx"
  }
  $insIdx = $ins.IndexOf("insert into $t (")
  if ($insIdx -lt 0) { $fail += "$t : no insert found in the pending file"; continue }
  $colsOpen  = $ins.IndexOf('(', $insIdx)
  $colsClose = Find-Balanced $ins $colsOpen
  $supplied  = ($ins.Substring($colsOpen + 1, $colsClose - $colsOpen - 1) -split ',') | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
  $valsIdx   = $ins.IndexOf('values', $colsClose)
  $valsOpen  = $ins.IndexOf('(', $valsIdx)
  $valsClose = Find-Balanced $ins $valsOpen
  $valuesRaw = $ins.Substring($valsOpen + 1, $valsClose - $valsOpen - 1)

  # count top-level values: a separator is a comma at paren depth 0 outside every
  # dollar-quoted literal and outside a line comment.
  $depth = 0; $n = 0; $i = 0; $inComment = $false
  while ($i -lt $valuesRaw.Length) {
    $ch = $valuesRaw[$i]
    if ($inComment) { if ($ch -eq "`n") { $inComment = $false }; $i++; continue }
    if ($ch -eq "`n") { $inComment = $false; $i++; continue }
    if ($ch -eq '-' -and ($i + 1) -lt $valuesRaw.Length -and $valuesRaw[$i + 1] -eq '-') { $inComment = $true; $i += 2; continue }
    if ($ch -eq '$') { $i = Skip-Quoted $valuesRaw $i; continue }
    if ($ch -eq '(') { $depth++ }
    if ($ch -eq ')') { $depth-- }
    if ($ch -eq ',' -and $depth -eq 0) { $n++ }
    $i++
  }
  $valueCount = $n + 1
  "    supplied=$($supplied.Count)  values=$valueCount"
  if ($supplied.Count -ne $valueCount) { $fail += "$t : $($supplied.Count) columns but $valueCount values" }

  foreach ($c in $supplied) { if (-not $cols.ContainsKey($c)) { $fail += "$t : column '$c' is not in the DDL" } }
  foreach ($c in $cols.Keys) {
    if ($cols[$c].notnull -and -not $cols[$c].hasdefault -and ($supplied -notcontains $c)) {
      $fail += "$t : NOT NULL column '$c' is neither supplied nor defaulted"
    }
  }

  # on conflict target must exist as a pk / unique in the same table body.
  # Located by index from just after the values block, not by regex - the first
  # regex version silently failed to match and therefore silently skipped this
  # check, which is the failure mode a validator must never have.
  $ocIdx = $ins.IndexOf('on conflict', $valsClose)
  if ($ocIdx -lt 0) { $fail += "$t : no on conflict clause found" }
  else {
    $ocOpen  = $ins.IndexOf('(', $ocIdx)
    $ocClose = Find-Balanced $ins $ocOpen
    $keys    = ($ins.Substring($ocOpen + 1, $ocClose - $ocOpen - 1) -split ',') | ForEach-Object { $_.Trim() }
    $have = @()
    $uniq = [regex]::Match($body, "unique \((?<k>.*?)\)", 'Singleline')
    $pk   = [regex]::Match($body, "primary key \((?<k>.*?)\)", 'Singleline')
    if ($uniq.Success) { $have += (($uniq.Groups['k'].Value -split ',') | ForEach-Object { $_.Trim() }) }
    if ($pk.Success)   { $have += (($pk.Groups['k'].Value   -split ',') | ForEach-Object { $_.Trim() }) }
    if ($have.Count -eq 0) { $fail += "$t : DDL declares no primary key or unique constraint at all" }
    $haveSig = (($have | Sort-Object) -join ',')
    $wantSig = (($keys | Sort-Object) -join ',')
    "    on conflict ($wantSig)  vs ddl constraints ($haveSig)"
    if ($haveSig -ne $wantSig) { $fail += "$t : on conflict ($wantSig) matches no primary key or unique constraint ($haveSig)" }
  }

  # every check constraint in this table, and the literal values I pass to it
  foreach ($c in [regex]::Matches($body, "check \((?<c>[^)]*?)\)", 'Singleline')) {
    "    check: " + ($c.Groups['c'].Value -replace '\s+',' ').Substring(0, [Math]::Min(120, ($c.Groups['c'].Value -replace '\s+',' ').Length))
  }
}

# --- 2. the two enum literals, checked against their check constraints ------
if ($ddl -notmatch "experiment_status in \('verified', 'unverified', 'pending', 'not-applicable'\)") { $fail += "experiment_status check constraint not found as expected" }
if ($ddl -notmatch "confidence in \('high', 'medium', 'low'\)") { $fail += "confidence check constraint not found as expected" }
if ($ins  -notmatch "'unverified'") { $fail += "the insert does not pass experiment_status = unverified" }
if ($ins  -notmatch "'low'") { $fail += "the insert does not pass confidence = low" }
if ($ins  -match "'measured'") { $fail += "the insert still passes the illegal value 'measured' somewhere" }
"--- experiment_status=unverified and confidence=low both present; 'measured' absent"

# --- 3. no credential material ---------------------------------------------
foreach ($pat in @('phx_','sk-','sbp_','service_role','Bearer ','eyJ')) {
  if ($ins.Contains($pat)) { $fail += "secret-shaped token '$pat' present" }
}
"--- secret scan clean"

if ($fail.Count -gt 0) { $fail | ForEach-Object { "FAIL: $_" }; exit 1 }
"PASS: insert matches the DDL it will run against"
