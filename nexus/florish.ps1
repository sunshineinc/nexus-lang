Param(
    [Parameter(Mandatory=$true)][string]$filePath
)

if (!(Test-Path $filePath)) {
    Write-Host "!ERR0 : " -ForegroundColor Red -NoNewline
    Write-Host "(ErroDeAcesso) Não foi possível encontrar o arquivo no caminho especificado."
}

else {
    & ".\interpreter.exe" $filePath
}

