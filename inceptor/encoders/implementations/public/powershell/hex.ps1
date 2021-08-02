function Invoke-HexDecode(){
    param(
        [Parameter(Mandatory=$True, Position=0)]
        [object] $Data
    )

    if ($Data.GetType().Name -eq "String"){
        [byte[]] $decoded = @($Data -split '(.{2})' | ForEach-Object {if (-not $_ -eq ""){ [byte]"0x$_"}})
        return $decoded
    }
}