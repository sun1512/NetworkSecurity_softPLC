PROGRAM PLC_PRG
VAR
    level : INT := 45;
    pump : BOOL;
	pump_memory : BOOL;
    valve : BOOL;
    request : BOOL;
    underflow : BOOL;
    overflow : BOOL;
    low_1 : INT := 40;
    high_1 : INT := 80;
END_VAR

underflow := level <= low_1;
overflow := level >= high_1;
IF NOT overflow AND (underflow OR pump_memory) THEN
    pump_memory := TRUE;
ELSIF overflow THEN
    pump_memory := FALSE;
END_IF;

pump := pump_memory;

valve := request AND (NOT underflow OR valve);

