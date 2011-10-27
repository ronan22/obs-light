# obslight completion script


_obslight() {
    local cur prev opts
    COMPREPLY=()
    OBSLIGHT="$(type -p obslight)"
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    #opts="--help --verbose --version"
    opts=`$OBSLIGHT --debug --debug --help`
    cmds=`$OBSLIGHT --debug --help`
    all_cmds=`$OBSLIGHT --debug --debug --debug --help`
    i=1
    while [ $i -le $COMP_CWORD ]
    do
       for OPT in $opts;do
           if [ $OPT == "${COMP_WORDS[i]}"  ] ; then
               all_cmds=`echo $all_cmds | sed "s/$OPT//g"`
           fi
       done 
       i=$(( $i + 1 ))
    done

    i=1
    while [ $i -le $COMP_CWORD ]
    do
       for cmd in $cmds;do
           if [ $cmd == "${COMP_WORDS[i]}"  ] ; then
                echo cms $cmd >> /tmp/test2del
                return 0
           fi
       done 
       i=$(( $i + 1 ))
    done
    if [[ ${cur} == * ]] ; then
        COMPREPLY=( $(compgen -W "${all_cmds}" -- ${cur}) )
        return 0
    fi
}

complete -F _obslight -o default obslight

