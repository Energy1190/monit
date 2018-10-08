#!/usr/bin/env sh

VM_NAMES="Virtual KVM Bochs HVM"
for VM in ${VM_NAMES}
do
    VM_CHECK=$(dmidecode -s system-product-name | grep $VM)
    if [ -n "$VM_CHECK" ]; then
        echo True > /.vm_status
    fi
done

python3 /app/init.py
monit -c /etc/monitrc -I -v