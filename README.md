# mzml2isa-qt
#####A PyQt interface for mzml2isa parser.

## Overview
This program is a Graphical User Interface for the [mzml2isa](https://github.com/althonos/mzml2isa) parser. It provides an easy-to-use interface to convert mzML files to an ISA-Tab Study. It was made with Python3 and PyQt5

## Install

### With PIP
If `pip` is present on your system (comes along most of Python install / releases), it can be used to install the program and its dependencies:
```bash
pip3 install mzml2isa-qt
```

### Without PIP
Once dependencies installed, clone the **mzml2isa-qt** repository to a folder with writing permissions:
```bash
git clone git://github.com/althonos/mzml2isa-qt
```

After that, either run the GUI directly: 
```bash
python3 run.py
```

Or install it locally to run with `mzmlisa-qt` command:
```bash
cd mzml2isa-qt && python3 setup.py install
```

## Use
Open the GUI with the `mzml2isa-qt` command. To simply parse **.mzML** files to **ISA**, select the directory containing your files. With default settings, the program will create the new ISA files in that folder, assuming the folder's name is the study identifier (_MTBSLxxx_ for instance for MetaboLights studies). This can be changed by unticking the `Export result to directory of each study` box. Once parameters are set up, click the `Convert` button to start the parser.

## MetaboLights
Generating a study to upload on MetaboLights requires pieces of information the parser cannot guess from the mzML file alone. To provide more metadata to your final ISA-Tab files, use the `Add Metadata` button to open a new window and update details about your study. Still, even with all the required fields filled, **the generated ISA needs to be enhanced after the end of the parsing** (using for instance [Metabolight pre-packaged ISA Creator](http://www.ebi.ac.uk/metabolights/) to add missing fields).

Missing information required for MetaboLights upload are at the moment:
* Study Factors (sample dependent, must be added to the _study_ file and to the _investigation_ file)
* Metabolite Assignment Files
* Study Designs

## TODO
* Either add a `metabolite assignment file` field to main window or change the **mzml2isa** parser behaviour so that it successfully detects metabolite assignment files and add them to the study file.

## License
GPLv3
