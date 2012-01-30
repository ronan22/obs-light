#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT server list
$OBSLIGHT server list reachable True
$OBSLIGHT server list reachable False
$OBSLIGHT server list --help

