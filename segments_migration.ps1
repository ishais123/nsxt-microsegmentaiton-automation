$path = Read-Host -Prompt "Please enter CSV file full path"
$pgs = Import-Csv -path $path


$cluster = Read-Host -Prompt "Please enter cluster name"

foreach ($pg in $pgs)
{
    $srcNet = $pg.src
    $dstNet = $pg.dst

    $vms = Get-VirtualPortGroup -Distributed | Where {$_.Name -eq $srcNet} | Get-VM
    $clusterVms = Get-Cluster -name $cluster | get-vm

    foreach ($vm in $vms)
    {
       if ($clusterVms.Contains($vm))
       {
        $adapters = get-vm $vm | Get-NetworkAdapter | Where {$_.networkname -eq $srcNet}
        foreach ($adapter in $adapters)
            {
                $old = $adapter.NetworkName
                $adapter | Set-NetworkAdapter -NetworkName $dstNet -Confirm:0 | out-null
                $new = $vm | Get-NetworkAdapter | Select-Object NetworkName
                write-host $vm "moved from" $old "to" $new
            } 
       }
    }
}
