#!/bin/bash

profile="Profile 34"
cd "$HOME/.config" && cp -r "google-chrome/$profile" "microsoft-edge/" && echo "Chrome profile successfully updated"
