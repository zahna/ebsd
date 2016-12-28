#!/bin/sh
# vim: set et ts=4 sw=4 sts=4
# Written by: Scott Zahn
# Date: 2008/03/06

# Make the Compact Flash disk image
# Note on partitioning:
# To find the total available blocks on a CF disk: 
# In linux, run fdisk -l <cf_device>
# with the actual CF card, which will show you the size in bytes.
# Make a disk image in BSD with dd, using the number of bytes as block size and count=1.
# Then register the file as an mfs disk.
# fdisk -I <device> will initialize the mfs disk with one partition spanning the whole disk.
# fdisk -s <device> will then show how many available blocks the device has.
# bsdlabel -w -e <device> will let you edit the disk label, then cut and paste to a file for later use.
#

HOME="/home/scott"
CFSIZE="256"
BUILDROOT="$HOME/ebsd"
CFROOT="$BUILDROOT/cffs"
GLUE="$BUILDROOT/glue"
CFG="$BUILDROOT/cfg"
TMP="/tmp"
MNT="/mnt"

export CFSIZE BUILDROOT CFROOT GLUE CFG TMP MNT

# This needs to be run as root
if [ `id -u` != 0 ]; then
    echo "$0 must be run as root. Exiting."
    exit 1
fi

# The temporary directory needs to exist
if [ ! -e "${TMP}" ]; then
    echo "${TMP} doesn't exist. Exiting."
    exit 1
fi

# Set the default umask
umask 002

# make the CF disk image
echo "* Creating CF disk image"
if [ "$CFSIZE" = "256" ]; then
#    dd if=/dev/zero of=$TMP/cf.img bs=258048000 count=1
    dd if=/dev/zero of=$TMP/cf.img skip=999 seek=999 bs=258048 count=1
fi
mdconfig -a -t vnode -f $TMP/cf.img -u 0

if [ $? = 0 ]; then
    # Slice and partition disk image
    echo "* Partitioning disk image"
    fdisk -I /dev/md0
    bsdlabel -R md0s1 ${BUILDROOT}/${CFSIZE}MB.ptbl

    # Install boot code
    echo "* Installing boot code"
    bsdlabel -B -b ${CFROOT}/boot/boot md0s1

    # Make filesystems on partitions
    echo "* Formatting partitions"
    newfs -b 4096 -f 512 -i 4096 -o space -m 0 md0s1a
    newfs -b 4096 -f 512 -i 4096 -o space -m 0 md0s1b
    newfs -b 4096 -f 512 -i 4096 -o space -m 0 md0s1d

    # Mount filesystems
    echo "* Mounting partitions"
    mount /dev/md0s1b $MNT
    mkdir $MNT/cfg
    mount /dev/md0s1a $MNT/cfg

    # Copy dist files
    echo "* Copying dist files"
    #tar -C ${CFROOT} -cf - . | tar -C $MNT -xf -
    cp -R ${CFROOT}/ $MNT

    # Copy glue files
    echo "* Copying glue files"
    #tar -C ${GLUE} -cf - . | tar -C $MNT -xf -
    cp -R ${GLUE}/ $MNT

    # Make /dev/null
    echo "* Creating /dev/null"
    mknod ${MNT}/dev/null c 0 27 root:wheel

    # Install config file here...
    # We use tar here to preserve special files like devices, etc
    echo "* Copying appliance config databases"
    #tar -C ${CFG} -cf - . | tar -C $MNT/cfg -xf -
    cp -R ${CFG}/* $MNT/cfg

    # Delete SVN checkout directories
    echo "* Stripping out .svn directories"
    find $MNT -name ".svn" | xargs rm -rf

    # Make root:wheel own it all
    echo "* Setting correct permissions on appliance filesystem"
    chown -R root:wheel $MNT 

    # Customize a few files & directories we need
    chmod 666 $MNT/dev/null
    #for i in $(grep -v "^#" ${FILELISTS}/perms); do
    #    dir=$(echo "$i" | cut -d' ' -f1)
    #    link=$(echo "$dir" | cut -d ":" -f 2)
    #    perms=$(echo "$i" | grep -oE "=[0-9]{3,4}" | cut -d'=' -f2-)
    #    owner=$(echo "$i" | grep -oE "%[a-z,A-Z,0-9,_,:]*" | cut -d'%' -f2)
    #done

    # Setting uid on just a few files
    chmod u+s $MNT/sbin/fastboot
    chmod u+s $MNT/sbin/shutdown

    # Unmount partitions
    umount /dev/md0s1a
    umount /dev/md0s1b

    # Unregister memory disk
    mdconfig -d -u 0

    # Move CF image to my home dir
    echo "Moving cf.img to $HOME"
    mv $TMP/cf.img $HOME

else
    echo "mdconfig disk creation failed. exiting."
    return 1
fi

return 0

