# Cardora smoke test — verifies backend and frontend are healthy
# Run from repo root: .\.claude\skills\run-cardora\smoke.ps1
# All checks should print PASS. Any FAIL means the app is not ready.

param(
    [string]$BackendUrl = "http://127.0.0.1:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

$pass = 0
$fail = 0

function Check {
    param([string]$Label, [scriptblock]$Test)
    try {
        $result = & $Test
        if ($result) {
            Write-Host "  PASS  $Label" -ForegroundColor Green
            $script:pass++
        } else {
            Write-Host "  FAIL  $Label" -ForegroundColor Red
            $script:fail++
        }
    } catch {
        Write-Host "  FAIL  $Label  [$($_.Exception.Message)]" -ForegroundColor Red
        $script:fail++
    }
}

Write-Host ""
Write-Host "=== Cardora Smoke Test ===" -ForegroundColor Cyan
Write-Host ""

# --- Backend checks ---
Write-Host "Backend ($BackendUrl)" -ForegroundColor Yellow

Check "GET /health returns status=healthy" {
    $r = Invoke-RestMethod "$BackendUrl/health" -TimeoutSec 5
    $r.status -eq "healthy"
}

Check "GET / returns welcome message" {
    $r = Invoke-RestMethod "$BackendUrl/" -TimeoutSec 5
    $r.message -like "*Cardora*"
}

Check "GET /docs returns HTML (Swagger UI)" {
    $r = Invoke-WebRequest "$BackendUrl/docs" -TimeoutSec 5 -UseBasicParsing
    $r.StatusCode -eq 200 -and $r.Content -like "*swagger*"
}

Check "GET /auth/login endpoint exists (405 = method not allowed, not 404)" {
    try {
        Invoke-RestMethod "$BackendUrl/auth/login" -Method GET -TimeoutSec 5
        $true
    } catch {
        # 405 Method Not Allowed means the route exists but GET isn't the right verb
        $_.Exception.Response.StatusCode.value__ -in @(405, 422)
    }
}

Check "POST /auth/login with bad creds returns 401/422 (route exists)" {
    try {
        Invoke-RestMethod "$BackendUrl/auth/login" -Method POST -Body (@{username="no@no.com"; password="bad"} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 5
        $false  # Should not succeed
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        $code -in @(401, 422)
    }
}

Check "GET /credit-cards returns 401 (protected route exists)" {
    try {
        Invoke-RestMethod "$BackendUrl/credit-cards" -TimeoutSec 5
        $false
    } catch {
        $_.Exception.Response.StatusCode.value__ -eq 401
    }
}

Check "GET /transactions returns 401 (protected route exists)" {
    try {
        Invoke-RestMethod "$BackendUrl/transactions" -TimeoutSec 5
        $false
    } catch {
        $_.Exception.Response.StatusCode.value__ -eq 401
    }
}

Check "GET /insights returns 401 (protected route exists)" {
    try {
        Invoke-RestMethod "$BackendUrl/insights" -TimeoutSec 5
        $false
    } catch {
        $_.Exception.Response.StatusCode.value__ -eq 401
    }
}

# --- Frontend checks ---
Write-Host ""
Write-Host "Frontend ($FrontendUrl)" -ForegroundColor Yellow

Check "GET / returns 200" {
    $r = Invoke-WebRequest "$FrontendUrl/" -TimeoutSec 10 -UseBasicParsing
    $r.StatusCode -eq 200
}

Check "GET /dashboard returns 200" {
    $r = Invoke-WebRequest "$FrontendUrl/dashboard" -TimeoutSec 10 -UseBasicParsing
    $r.StatusCode -eq 200
}

Check "GET /login returns 200" {
    $r = Invoke-WebRequest "$FrontendUrl/login" -TimeoutSec 10 -UseBasicParsing
    $r.StatusCode -eq 200
}

# --- Summary ---
Write-Host ""
$total = $pass + $fail
if ($fail -eq 0) {
    Write-Host "All $total checks passed." -ForegroundColor Green
} else {
    Write-Host "$fail/$total checks FAILED." -ForegroundColor Red
    exit 1
}
Write-Host ""
