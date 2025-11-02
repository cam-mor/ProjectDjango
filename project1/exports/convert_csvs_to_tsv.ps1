# convert_csvs_to_tsv.ps1
# Convierte todos los .csv en la carpeta actual a .tsv usando Import-Csv/Export-Csv
# Esto preserva campos entrecomillados y comas internas.
# Uso:
#   cd C:\Users\iamxa\Desktop\ProjectDjango\project1\exports
#   .\convert_csvs_to_tsv.ps1

$files = Get-ChildItem -Path . -Filter *.csv
foreach ($f in $files) {
    Write-Host "Converting $($f.Name) -> $($f.BaseName).tsv"
    try {
        $data = Import-Csv -Path $f.FullName -Encoding UTF8
        $outPath = Join-Path $f.DirectoryName ($f.BaseName + '.tsv')
        # Export without quotes, use tab delimiter
        $data | Export-Csv -Path $outPath -Delimiter "`t" -NoTypeInformation -Encoding UTF8
    } catch {
        Write-Host "Error converting $($f.Name): $_" -ForegroundColor Red
    }
}
Write-Host "Done. Generated TSV files in current folder." -ForegroundColor Green
