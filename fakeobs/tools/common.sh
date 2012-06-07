
RED="\e[31;1m"
GREEN="\e[32;1m"
YELLOW="\e[33;1m"
DEFAULT="\e[0m"


function echo_red()
{
  echo -e $RED$@$DEFAULT
}

function echo_green()
{
  echo -e $GREEN$@$DEFAULT
}

function echo_yellow()
{
  echo -e $YELLOW$@$DEFAULT
}

PROJECTINFOFILE="project_info"
