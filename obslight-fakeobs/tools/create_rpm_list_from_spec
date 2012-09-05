#!/bin/bash
ADDPACKAGES=" "
while test -n "$1" ; do
    case "$1" in
        --repository|--repo)
            repos[${#repos[@]}]="$2";
            shift 2;
            ;;
        --dist)
            DIST="$2";
            shift 2;
            ;;
        --depfile)
            CACHE_FILE="$2";
            shift 2;
            ;;
        --spec)
            SPEC="$2";
            shift 2;
            ;;
        --archpath)
            ARCHPATH="$2";
            shift 2;
            ;;
        --addPackages)
            ADDPACKAGES=$ADDPACKAGES" $2";
            shift 2;
            ;;

        --stderr)
            STDERR="$2";
            shift 2;
            ;;
        --stdout)
            STDOUT="$2";
            shift 2;
            ;;
        *)
            break
            ;;
    esac
done

BUILD_RPMS=
SRC=
LIST_STATE=
BUILD_DIR=/usr/lib/build
CACHE_DIR=/var/cache/build

getcachedir()
{
    url=$1
    case $url in
      *.pkg.tar.?z) url="arch@$url" ;;
    esac
    for repo in "${repos[@]}" ; do
        if [ "${url:0:${#repo}}" == "$repo" -o "${url:0:${#repo}}" == "$repo" ] ; then
            read repoid dummy < <(echo -n "$repo" | md5sum)
            echo "$CACHE_DIR/$repoid"
            break
        fi
    done
}

validate_cache_file()
{
    local findonly=''
    
    if ! test -f $CACHE_FILE || ! test -f $CACHE_FILE.id || \
        test "${repos[*]} ${BUILD_RPMS//:/ /}" != "$(cat $CACHE_FILE.id 2>/dev/null)"; then
        rm -f $CACHE_FILE.id
    else
        for SRC in "${repos[@]}" ${BUILD_RPMS//:/ /}; do
            test -n "$SRC" || SRC=.
            if [ "${SRC#zypp://}" != "$SRC" ]; then
                SRC="/var/cache/zypp/raw" # XXX can't use name here as we'd need to parse the file
            fi
            if test "$SRC" -nt $CACHE_FILE; then
                rm -f $CACHE_FILE.id
                break
            fi
        done
    fi

    if ! test -f $CACHE_FILE.id ; then
        test -z "$LIST_STATE" && echo initializing $CACHE_FILE ...
        for SRC in "${repos[@]}" -- ${BUILD_RPMS//:/ /}; do
            if test "$SRC" = '--' ; then
                findonly=1
                continue
            fi
            test -z "$SRC" && SRC=`pwd`
            if [ "${SRC#zypp://}" != "$SRC" ]; then
                set -- $BUILD_DIR/createrepomddeps "$SRC"
            elif [ "${SRC#http://}" != "$SRC" -o "${SRC#https://}" != "$SRC" -o "${SRC#ftp://}" != "$SRC" -o "${SRC#ftps://}" != "$SRC" ]; then
                mkdir -p "$(getcachedir "$SRC")"

                set -- $BUILD_DIR/createrepomddeps --cachedir="$CACHE_DIR" "$SRC"
            elif [ "${SRC#arch@http://}" != "$SRC" -o "${SRC#arch@https://}" != "$SRC" -o "${SRC#arch@ftp://}" != "$SRC" -o "${SRC#arch@ftps://}" != "$SRC" ]; then
                mkdir -p "$(getcachedir "$SRC")"
                set -- $BUILD_DIR/createrepomddeps --cachedir="$CACHE_DIR" "$SRC"
            elif [ ! -e "$SRC" ]; then
                exit 1
            elif [ -z "$findonly" -a -e "$SRC"/suse/setup/descr/packages -o -e "$SRC"/suse/setup/descr/packages.gz ]; then
                set -- $BUILD_DIR/createyastdeps "$SRC"
            elif [ -z "$findonly" -a -e "$SRC"/repodata/repomd.xml ]; then
                set -- $BUILD_DIR/createrepomddeps "$SRC"
            else
                set -- $BUILD_DIR/createrpmdeps "$SRC"
            fi
            echo "$@" >&2
            "$@" || exit 1
            echo D:
        done > $CACHE_FILE.new

        mv $CACHE_FILE.new $CACHE_FILE
        echo "${repos[*]} ${BUILD_RPMS//:/ /}" > $CACHE_FILE.id
    fi
}

validate_cache_file
tools/expanddeps --dist $DIST --depfile $CACHE_FILE --archpath $ARCHPATH --configdir /usr/lib/build/configs $ADDPACKAGES $SPEC >$STDOUT 2>$STDERR
exit 0

