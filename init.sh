#!/usr/bin/env sh

VM_NAMES="Virtual KVM Bochs HVM"
for VM in ${VM_NAMES}
do
    VM_CHECK=$(dmidecode -s system-product-name | grep $VM)
    if [ -n "$VM_CHECK" ]; then
        echo True > /.vm_status
    fi
done

python3 /app/init.py --templates /app/templates --includes /app/includes
if [ $? != 0 ]; then
    echo "Error on generate config. Exit."
	exit 1
fi
monit -c /etc/monitrc -I -v