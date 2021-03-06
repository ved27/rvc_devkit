#!/bin/sh
# Converts GT from OID into COCO format
# requires git, python and pycocotools which can be installed via:
# pip install pycocotools
# (use gitbash for MS Windows)

RVC_OBJ_DET_SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# All data is downloaded to subfolders of RVC_DATA_DIR; if this is not defined: use the root dir + /datasets
if [ -z "${RVC_DATA_DIR}" ]; then
  RVC_DATA_SRC_DIR=${RVC_OBJ_DET_SCRIPT_DIR}/../datasets/
else
  RVC_DATA_SRC_DIR=${RVC_DATA_DIR}/
fi

if [ -z "${RVC_JOINED_TRG_DIR}" ]; then
  RVC_DATA_TRG_DIR=${RVC_DATA_SRC_DIR}/
else
  RVC_DATA_TRG_DIR=${RVC_JOINED_TRG_DIR}/
fi

#check if oid has already been converted 
if [ ! -f "$RVC_DATA_SRC_DIR/oid/annotations/openimages_challenge_2019_train_bbox.json" ]; then
  echo "Converting OID to COCO format..."
  if [ ! -d $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco ]; then
  # getting defined version of openimages2coco repo
    git -C $RVC_OBJ_DET_SCRIPT_DIR clone https://github.com/bethgelab/openimages2coco.git 
    git -C $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco checkout 15e708ee8f803c09e5154094645c15e7001365a0
  fi
  
  #remapping OID format to COCO
  pushd $RVC_OBJ_DET_SCRIPT_DIR/openimages2coco/
  python convert.py --path $RVC_DATA_SRC_DIR/oid/ --version challenge_2019
  popd
fi

RVC_DATA_TRG_DIR=
RVC_DATA_SRC_DIR=
RVC_OBJ_DET_SCRIPT_DIR=

echo "Finished remapping."
