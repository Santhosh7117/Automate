#!/bin/bash

lspci | grep -i unknown
lspci | grep -i Error
lspci -vvv | grep -i unknown
