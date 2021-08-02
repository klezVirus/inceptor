function Invoke-NopDecode {
    [CmdletBinding()]

    param
    (
        [Parameter(Mandatory=$True)]
        [byte[]]$Data
    )
    [byte[]] $encoded = [System.Byte[]]::new(($Data.Length+1)/2)
    $j = 0
    for ($i = 0; $i -lt $Data.length; $i++) {
        if ($i%2 -eq 0){
            $encoded[$j] = $Data[$i]
            $j++
        }
    }
    return $encoded
}