for file in qt/*.ui; do 
	echo "$file > ${file%.*}.py"
	pyuic5 $file > ${file%.*}.py
done

for file in qt/*.qrc; do
	echo "$file > ${file%.*}_rc.py"
        pyrcc5 $file > ${file%.*}_rc.py
done