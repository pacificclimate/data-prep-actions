for file in /local_temp/path/to/data/prsn*.nc
do 
  echo "processing $file"
  ncatted -a missing_value,prsn,m,s,-32768 $file $file.1
  ncatted -a _FillValue,prsn,m,s,-32768 $file.1 $file.2
  mv $file $file.old
  mv $file.2 $file
  rm $file.1
done
