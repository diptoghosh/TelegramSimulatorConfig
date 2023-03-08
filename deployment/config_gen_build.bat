REM Removing old files
RD /S /Q ".\dist"

pyinstaller --noconsole --onefile --noconfirm  ^
	--icon=".\icon\sms-logo-transparent.ico"  ^
	--exclude-module altgraph ^
	--exclude-module beautifulsoup4 ^
	--exclude-module soupsieve ^
	--add-data="..\sms-logo-transparent.ico";"." ^
	--add-data="..\CreateFormattedCsv.py";"." ^
	--version-file .\version\csv_gen_version.rc ^
	--name=CsvGenerator ..\CsvGenerator.py

RD /S /Q ".\build"
