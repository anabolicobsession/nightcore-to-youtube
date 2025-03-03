#!/bin/bash


# define alias and script location
ALIAS="nightcore-to-youtube"
SCRIPT="$(dirname $(realpath "$0"))/nightcore_to_youtube.sh"
RC="$HOME/.bashrc"


if ! grep -q "alias $ALIAS=" "$RC"; then
    echo "Creating alias for script: $SCRIPT"
    echo "" >> "$RC"  # add blank line before alias
    echo "alias $ALIAS='$SCRIPT'" >> "$RC"
else
    echo "Alias already exists"
fi

source "$RC"  # reload RC to apply changes
echo "You can now use '$ALIAS' to run the script"
