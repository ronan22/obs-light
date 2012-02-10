# obslight completion script

_obslight() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"

    SYS_ARG=""
    SPC=" "
    i=1
    while [ $i -le $(($COMP_CWORD -1)) ]
    do 
       SYS_ARG=$SYS_ARG$SPC${COMP_WORDS[i]}
       i=$(( $i + 1 ))
    done
    all_cmds=`obslight noaction $SYS_ARG`

    COMPREPLY=( $(compgen -W "${all_cmds}" -- ${cur}) )
}

complete -F _obslight -o default obslight

