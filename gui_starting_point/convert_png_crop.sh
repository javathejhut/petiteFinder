#!/bin/bash
TOTAL_TIFF="$(ls -1q *.tiff | wc -l)"
echo -e "converting to png grayscale"
var=0

for f in *.tiff; do 

convert $f -colorspace Gray "${f%.tiff}_gray.png"

echo -e "fraction complete: \n";
var=$((var+1));

#echo "scale=2; ($var/$TOTAL)" | bc -l;
echo "$var/$TOTAL_TIFF";
echo -e "\n";
done

TOTAL_GRAY="$(ls -1q *gray.png | wc -l)"
echo -e "cropping pngs"
var=0

for g in *gray.png; do 

convert $g -crop 4752x4576+584+144 "${g%.png}_l1.png"
convert $g -crop 4752x4576+5344+144 "${g%.png}_l2.png"
convert $g -crop 4752x4576+584+4782 "${g%.png}_l3.png"
convert $g -crop 4752x4576+5344+4782 "${g%.png}_l4.png"
convert $g -crop 4752x4576+5200+9264 "${g%.png}_l5.png"

echo -e "fraction complete: \n";
var=$((var+1));

echo "$var/$TOTAL_GRAY";
echo -e "\n";
done
