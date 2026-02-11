#!/bin/sh -e

if [ ! -f ./main.pyw ]; then
    echo main.pyw is missing
    exit
fi

pip install PyInstaller

SOURCE_DIR=$PWD
CURRENT_DIR_NAME=$(basename "$PWD")
INSTALL_DIR=~/pyinstaller_$CURRENT_DIR_NAME
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR
pyinstaller --name $CURRENT_DIR_NAME "$SOURCE_DIR/main.pyw"
