#!/bin/bash

RED="\e[31;1m"
GREEN="\e[32;1m"
YELLOW="\e[33;1m"
DEFAULT="\e[0m"

FAKEOBSPREFIX="/srv/fakeobs"
GRABINFOFILE="grab_info"
PROJECTINFOFILE="project_info"
CURLARGS="-k --retry 5"

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

function fix_api()
{
  local orig_api="$1"
  if ! $(echo $orig_api | grep -q "/public$")
  then
    echo $orig_api/public
  else
    echo $orig_api
  fi
}

function check_public_api()
{
  local api="$1"
  local url="$api/distributions"
  echo_green "Checking API '$url'..."
  curl -s -S -f -k $url 1>/dev/null 2>error.log
  if [ "$?" -ne "0" ]
  then
    echo_red " '$api' does not seem to be an OBS public API (or it is down)"
    cat error.log
    return 1
  else
    echo_green " '$api' is an OBS public API"
    rm -f error.log
    return 0
  fi
}

function check_rsync_url()
{
  local url=$1
  echo_green "Checking rsync URL '$url'..."
  echo $url | grep -E -q "^rsync:\/\/"
  if [ "$?" -ne "0" ]
  then
    echo_red "rsync URL does not start with 'rsync://': '$url'"
    return 1
  fi
  rsync -q $url
  if [ "$?" -ne "0" ]
  then
    echo_red "Failed to reach '$url'. See above message for details."
    return 1
  fi
  echo_green " OK"
  return 0
}

function project_exists()
{
  local project=$1
  SANITIZEDNAME=`echo $project | sed y,:,_,`
  grep -s "project=\"$project\"" mappings.xml
  local exists_in_mappings=$?
  local git_repos_count=`[ -d "packages-git/$SANITIZENAME" ] && ls -1 "packages-git/$SANITIZENAME" | wc -l || echo 0`
  [ "$git_repos_count" -gt "0" ]
  local has_git_repos=$?
  return $exists_in_mappings
}

function project_exists_on_server()
{
  local api=$1
  local project=$2
  local url="$1/build/$project"
  curl -s -S -f -k $url 1>/dev/null 2>error.log
  if [ "$?" -ne "0" ]
  then
    echo_red "'$project' does not seem to be an OBS project"
    cat error.log
    return 1
  else
    echo_green "'$project' exists on server"
    rm -f error.log
    return 0
  fi
}

function target_exists_on_server()
{
  local api=$1
  local project=$2
  local target=$3
  local url="$1/build/$project/$target"
  curl -s -S -f -k $url 1>/dev/null 2>error.log
  if [ "$?" -ne "0" ]
  then
    echo_red "Invalid target '$target' for project '$project'"
    curl -k "$1/build/$project"
    return 1
  else
    echo_green "Target '$target' exists for project '$project'"
    rm -f error.log
    return 0
  fi
}

function arch_exists_on_server()
{
  local api=$1
  local project=$2
  local target=$3
  local arch=$4
  local url="$1/build/$project/$target/$arch/"
  curl -s -S -f -k $url 1>/dev/null 2>error.log
  if [ "$?" -ne "0" ]
  then
    echo_red "Invalid arch '$arch' for project '$project'"
    curl -k "$1/build/$project/$target"
    return 1
  else
    echo_green "Arch '$arch' exists for project '$project'"
    rm -f error.log
    return 0
  fi
}

function clean_old_mappings()
{
  # Keep the 3 most recent backups
  local mappings=`ls -1 mappings.xml.* | sort | head -n -3`
  if [ -n "$mappings" ]
  then
    rm -f $mappings
#    echo_yellow "We found old mappings files:\n$mappings"
#    echo_yellow "Do you want to remove them ? [Y/n] "
#    # '-l' is for lowercase
#    declare -l answer
#    read answer
#    [ "$answer" != "n" ] && rm -f $mappings
  fi
}

function print_rpm_names()
{
  local name_file="$1"
  sed -r -n "s,.*\"(.*\.rpm)\".*,\1,p" $name_file
}

function check_missing_files()
{
  local file_list_file="$1"
  local directory="$2"
  local missing_files=""
  [ -n "$directory" ] && cd "$directory"
  for filename in `cat $file_list_file`
  do
    [ -f "$filename" ] || missing_files="$missing_files $filename"
  done

  if [ -n "$missing_files" ]
  then
    echo "$missing_files"
    return 1
  else
    return 0
  fi
}
