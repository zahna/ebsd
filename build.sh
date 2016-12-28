#!/usr/bin/env bash
# vim: set et ts=4 sw=4 sts=4
# This is the automation script for the building the CF filesystem.
# Written by: Scott Zahn
# Date: 2007/04/28

BUILDROOT="$HOME/ebsd"
CFROOT="$BUILDROOT/cffs"
CFG="$BUILDROOT/cfg"
FILELISTS="$BUILDROOT/filelists"
TMP="/tmp"

export BUILDROOT CFROOT CFG FILELISTS TMP

#if [ `id -u` != 0 ]; then
#    echo "$0 must be run as root. Exiting."
#    exit 1
#fi

##### FUNCTIONS #####

make_dirs() {
    echo "Creating directory structure for CF card."

    # Create the cfroot directory, if needed
    [ ! -d ${CFROOT} ] && mkdir ${CFROOT}

    for i in `grep -v "^#" ${FILELISTS}/systemdirs`; do
        dir=$(echo "$i" | cut -d ":" -f 1)
        [ ! -d ${CFROOT}$dir ] && mkdir -v ${CFROOT}/$dir

        # Deal with links
        if [ $(echo "$i" | grep -c ":") -gt 0 ]; then
            for j in $(echo $i | cut -d ":" -f 2- | sed "s/:/ /g"); do
                [ -L ${CFROOT}$j ] && rm ${CFROOT}$j
                ln -sv $dir ${CFROOT}$j
            done
        fi
    done
    return 0
}

copy_bins() {
    FILESET="$1" 
    echo "Adding $FILESET files:"

    # Make sure the file list exists
    if [ ! -e "${FILELISTS}/${FILESET}" ]; then
        echo "${FILELISTS}/${FILESET} doesn't exist"
        return 1
    fi

    # Create the cfroot directory, if needed
    if [ "$FILESET" = "system" ]; then
        [ -d "${CFROOT}" ] || mkdir ${CFROOT}
    fi

    # Copy the binaries
    for i in $(grep -v "^#" ${FILELISTS}/${FILESET}); do
        if [ "${i:0:1}" != "/" ]; then
            eval "$i"
        else
            file=$(echo "$i" | cut -d ":" -f 1)

            if [ ! -f "${CFROOT}$file" ]; then
                # Deal with absent directories
                dir=$(dirname $file)
                [ ! -d ${CFROOT}$dir ] && mkdir -pv ${CFROOT}$dir
                cp -v $file $(dirname ${CFROOT}$file)

                # Deal with links
                if [ $(echo "$i" | grep -c ":") -gt 0 ]; then
                    for j in $(echo $i | cut -d ":" -f 2- | sed "s/:/ /g"); do
                        [ -L ${CFROOT}$j ] && rm ${CFROOT}$j
                        ln -sv $file ${CFROOT}$j
                    done
                fi
            elif [ -e "$file" ] && [ "$(md5 -q $file)" != "$(md5 -q ${CFROOT}$file)" ]; then
                cp -v $file $(dirname ${CFROOT}$file)
            fi
            
            #mod=$(echo "$i" | cut -d " " -f 2)
            #if [ -n $mod ]; then
            #    chmod $mod ${CFROOT}$file
            #fi
        fi
    done

    # Remind the user to manually copy the custom binaries
    echo -e "\nDon't forget to update (if necessary):"
    echo "/boot/device.hints (found at /usr/src/sys/i386/conf/GENERIC.hints)"
    echo "/usr/local/bin/mailsend"
    echo "/usr/local/sbin/clog"
    echo "/usr/local/sbin/syslogd"

    return 0
}

# Adding the libraries
copy_libs() {
    echo "Adding required libs:"

    [ -f $TMP/lib.list ] && rm -f $TMP/lib.list

    # Identify required libs.
    for file in `find -X $CFROOT -type f 2> /dev/null`; do
        #echo "# $file:\n" >> $TMP/lib.list
        ldd -f "%p\n" $file 2> /dev/null >> $TMP/lib.list
    done

    # Copy required libs.
    for i in `grep "^/" $TMP/lib.list | sort -u`; do
        if [ ! -f ${CFROOT}$i ]; then
            # Deal with directories
            dir=$(dirname $i)
            [ ! -d ${CFROOT}$dir ] && mkdir -pv ${CFROOT}$dir
            cp -v $i ${CFROOT}$i
        elif [ "$(md5 -q $i)" != "$(md5 -q ${CFROOT}$i)" ]; then
            cp -v $i ${CFROOT}$i
        fi
    done

    # Cleanup.
    rm -f ${TMP}/lib.list

    return 0
}

compileall() {
    echo "Compiling all python under ${CFROOT}"
    python /usr/local/lib/python2.5/compileall.pyo  ${CFROOT}
}

main() {
    read -p '
Welcome to the appliance build environment.
Main Menu:

0  - Make cf root directory structure
1  - Copy OS binaries in config to cfroot/
2  - Copy necessary libraries to cfroot/
----
9  - Compile all python code in cfroot
*  - Quit
> ' choice

    case $choice in
        0)  make_dirs;;
        1)  copy_bins "system";;
        2)  copy_libs;;
        9)  compileall;;
        *)  exit 0;;
    esac

    [ $? = 0 ] && echo "=> Successful" || echo "=> Failed"
    sleep 1

    return 0
}

while true; do
    main
done
exit 0
