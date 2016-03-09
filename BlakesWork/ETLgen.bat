@echo off
ECHO These commands will enable tracing:
@echo on
logman.exe create trace "NT Kernel Logger" -p "Windows Kernel Trace" (cswitch,thread,process) -ow -o %~dp0\log.etl
logman.exe start "NT Kernel Logger"
@echo off
echo
ECHO Enter any key to stop tracing
@echo on
pause
logman.exe stop "NT Kernel Logger"
logman.exe delete "NT Kernel Logger"
tracerpt %~dp0\log_000001.etl -o %~dp0\log.csv -of CSV
@echo off
echo Tracing has been captured and saved successfully
pause