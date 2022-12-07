#!/bin/bash
# Usage: ./pylas.sh [cram-or-bam-file] [ref-genome-for-cram-file]

file=$1
file_ext=$(basename "${file}")
file_ext=${file_ext##*.}
file_raw=$(basename "${file}")
file_raw=${file_raw%.$file_ext}
reference=$2

function log {
  echo -e "\033[0;33m$1\033[0m"
}

log "Start: [$(date)]"

# --------------------------------------------------------------------------- #
# 1. Download `mosdepth` + `bed2cov` + `pylas.py`

if [ ! -f './mosdepth' ]; then
  wget "https://github.com/brentp/mosdepth/releases/download/v0.3.3/mosdepth"
  chmod +x './mosdepth'
fi
if [ ! -f './bed2cov' ]; then
  wget "https://github.com/comp-bio/Bed2Cov/raw/main/build/bed2cov_$(uname)" -O ./bed2cov
  chmod +x './bed2cov'
fi
if [ ! -f './pylas.py' ]; then
  wget "https://raw.githubusercontent.com/comp-bio/PyLAS/main/pylas.py"
fi

# --------------------------------------------------------------------------- #
# 2. Python3 deps

python3 -c "import pywt" 2>&- || pip install PyWavelets
python3 -c "import numpy" 2>&- || pip install numpy

# --------------------------------------------------------------------------- #
# 3. Extract depth-of-coverage from .cram files

if [ ! -f "${file_raw}.per-base.bed.gz" ]; then
  log "Extracting depth-of-coverage. Ext:${file_ext}"
  if [ ${file_ext} == "cram" ]; then ./mosdepth -t 24 -f "${reference}" "${file_raw}" "${file}"; fi
  if [ ${file_ext} == "bam"  ]; then ./mosdepth -t 24 "${file_raw}" "${file}"; fi
fi

# --------------------------------------------------------------------------- #
# 4. Converting depth-of-coverage (.bed.gz) to .bcov

log "Converting .bed.gz -> .bcov"
mkdir -p "${file_raw}"
# shellcheck disable=SC2164
cd "${file_raw}"
gzip -cd ../"${file_raw}".per-base.bed.gz | ../bed2cov
rm -f ./*_*.bcov ./*HLA*.bcov ./*EBV.bcov GL00*.bcov hs37d5.bcov
cd ../

# --------------------------------------------------------------------------- #
# 5. Calculate LAS

rm -f ${file_raw}/*.las
for bc in $(ls ${file_raw}/*.bcov); do
  python3 pylas.py "${bc}" > "${bc}.las";
done

echo "Chromosome_name Start End FFT_dF DTCWT_Entropy LAS Description" > ${file_raw}.las
for las in $(ls -1v ${file_raw}/*.las); do
  cat $las >> ${file_raw}.las
done

# --------------------------------------------------------------------------- #
log "Done: [$(date)]"
log "Result: ${file_raw}.las"
