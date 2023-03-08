REM Removing old files
RD /S /Q ".\dist"

pyinstaller --noconsole --onefile --noconfirm  ^
	--icon=".\icon\sms-logo-transparent.ico"  ^
	--exclude-module altgraph ^
	--exclude-module beautifulsoup4 ^
	--exclude-module soupsieve ^
	--add-data="..\sms-logo-transparent.ico";"." ^
	--add-data="..\TelegramHandler.py";"." ^
	--add-data="..\SimDataHandler.py";"." ^
	--version-file .\version\version.rc ^
	--name=TelegramSimulator ..\SimulatorUI.py

COPY "..\config.INI" ".\dist\"
RD /S /Q ".\build"
