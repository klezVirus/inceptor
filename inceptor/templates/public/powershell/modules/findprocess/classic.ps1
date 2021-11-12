
function ####FUNCTION####{
    $processes = @(
        ####PROCESS####
    )
    $processes | ForEach-Object {
        $list = (Get-Process $_ -ErrorAction SilentlyContinue)
        if ($list.Length -gt 0){
            return $list[0].Id
        }
    }
}
