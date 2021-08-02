####CODE####

$encoded = <####SHELLCODE####>

####CALL####

$path = ####FILE####
[System.IO.File]::WriteAllBytes($path, $decoded)
