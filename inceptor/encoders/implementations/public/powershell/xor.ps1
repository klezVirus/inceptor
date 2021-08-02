function Invoke-Xor {
    [CmdletBinding()]

    param
    (
        [Parameter(Mandatory=$True)]
        [byte[]]$Data
    )
    $key = [System.Text.Encoding]::UTF8.GetBytes("####KEY####")

    $encoded = $(for ($i = 0; $i -lt $Data.length; ) {
        for ($j = 0; $j -lt $key.length; $j++) {
            $Data[$i] -bxor $key[$j]
            $i++
            if ($i -ge $Data.Length) {
                $j = $key.length
            }
        }
    })

    return $encoded
}