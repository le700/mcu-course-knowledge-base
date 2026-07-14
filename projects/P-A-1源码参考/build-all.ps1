[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$projects = @(
    'step03_led_half',
    'step04_switch_led',
    'step05_display_4523',
    'step06_adc_led',
    'step07_adc_temp',
    'step09_uart_echo',
    'pa1_main'
)

foreach ($project in $projects) {
    Write-Host ''
    Write-Host "===== Build $project ====="
    & (Join-Path $PSScriptRoot 'build-project.ps1') -Project $project
}

$buildTool = 'C:\Users\28011\Documents\Codex\2026-07-03\new-chat\outputs\keil-proteus-automation\scripts\Build-C51.ps1'
$diagnostics = @(
    @{
        Name = 'diag_dht11_display'
        Sources = @(
            'diagnostics\src\diag_dht11_display.c',
            'common\i8255.c',
            'common\display.c',
            'common\dht11.c',
            'common\delay.c'
        )
    },
    @{
        Name = 'diag_dht11_error'
        Sources = @(
            'diagnostics\src\diag_dht11_error.c',
            'common\i8255.c',
            'common\display.c',
            'common\dht11.c',
            'common\delay.c'
        )
    },
    @{
        Name = 'diag_dht11_bitpos'
        Sources = @(
            'diagnostics\src\diag_dht11_bitpos.c',
            'common\i8255.c',
            'common\display.c',
            'common\dht11.c',
            'common\delay.c'
        )
    },
    @{
        Name = 'diag_dht11_rawbytes'
        Sources = @(
            'diagnostics\src\diag_dht11_rawbytes.c',
            'common\i8255.c',
            'common\display.c',
            'common\dht11.c',
            'common\delay.c'
        )
    },
    @{
        Name = 'diag_p33_toggle'
        Sources = @(
            'diagnostics\src\diag_p33_toggle.c'
        )
    },
    @{
        Name = 'diag_display_format'
        Sources = @(
            'diagnostics\src\diag_display_format.c',
            'common\i8255.c',
            'common\display.c',
            'common\delay.c'
        )
    }
)

foreach ($diag in $diagnostics) {
    $diagName = $diag.Name
    $diagSources = @($diag.Sources | ForEach-Object { Join-Path $PSScriptRoot $_ })

    Write-Host ''
    Write-Host "===== Build $diagName ====="
    & $buildTool `
        -ProjectDir (Join-Path $PSScriptRoot 'diagnostics') `
        -ProjectName $diagName `
        -Sources $diagSources `
        -IncludeDirs @((Join-Path $PSScriptRoot 'common')) `
        -BuildDir (Join-Path $PSScriptRoot "diagnostics\build\$diagName") `
        -HexCopyPath (Join-Path $PSScriptRoot "diagnostics\hex\$diagName.hex")
}

Write-Host ''
Write-Host 'All P-A-1 projects built.'
