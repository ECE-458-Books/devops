#!/usr/bin/env bash

# ----------------------------------------------------------------------
# Copyright © 2023 Hosung Kim <hk196@duke.edu>
#
# All rights reserved
# ----------------------------------------------------------------------

# A better class of script... [https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/]
set -o errexit          # Exit on most errors (see the manual)
set -o errtrace         # Make sure any error trap is inherited
set -o nounset          # Disallow expansion of unset variables
set -o pipefail         # Use last non-zero exit code in a pipeline

#set -e			# Exit immediately when command fails
set -u 			# Treat unset variables as error
set -E			# ERR traps are inherited
#set -x			# Print the command executed

# ---------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------
Main()
{

# Find current user and do not add
u="$USER"

# Find current system users
users=$(awk -F':' '{print $1}' /etc/passwd)

currusers=($users)

# Get next available UID
uid=$(getent passwd | awk -F: '($3>600) && ($3<10000) && ($3>maxuid) { maxuid=$3; } END { print maxuid+1; }')

printf 'Current user is %s\n' "$u" 

# Clone git repo for user add [https://vcm.duke.edu/help/24]
git clone https://gitlab.oit.duke.edu/devil-ops/users.git &>/dev/null
cd users

# Add users except for current user
for user in ${teammates[@]}
do
if [[ "$user" != "$u" ]]; then
  if [[ " ${currusers[*]} " =~ " ${user} " ]]; then
    printf '%s is already a user in this system\n' "$user"
  else
    printf 'Adding %s with uid: %d\n' "$user" "$uid"
    sudo ./install.sh -a yes -u $uid $user &>/dev/null

    if [ $? -eq 0 ]; then
    	printf 'Added %s:%d with admin privileges\n' "$user" "$uid"
    	((uid+=1))
    else
    	printf 'Failed to add %s:%d with admin privileges\n' "$user" "$uid"
    fi

  fi
fi
done

cd ..

# Delete Git Repo for adding users
rm -rf users
}

Help()
{
   # Display Help
   echo "Script to add users to Duke VCM through NetIDs"
   echo
   echo "Syntax: ./addusers.sh [-h] [-u \"[NetIDs whitespace separated]\"]"
   echo "options:"
   echo "h     Print this Help."
   echo "u     List NetIDs that need to be added in one string"
   echo
}

# ---------------------------------------------------------------------
# Main body of script starts here
# ---------------------------------------------------------------------
while getopts ":hu:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      u) # Enter Users
	 userargs=${OPTARG}
	 teammates=($userargs)
	 Main
	 exit;;
      \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

Help
