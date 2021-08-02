function Invoke-Base64Decode(){
    param(
        [Parameter(Mandatory=$True, Position=0)]
        [object] $Data
    )

    if ($Data.GetType().Name -eq "String"){
        return ([System.Convert]::FromBase64String($Data))
    }
    elseif ($Data.GetType().Name -eq "Byte[]"){
        return ([System.Convert]::FromBase64String([Encoding.UTF8]::GetString($Data)))
    }
}