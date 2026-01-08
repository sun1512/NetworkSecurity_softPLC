PROGRAM PLC_PRG
VAR
    level : INT := 45;
    pump : BOOL;
    valve : BOOL;
    request : BOOL;
    underflow : BOOL;
    overflow : BOOL;
    low_1 : INT := 40;
    high_1 : INT := 80;
	pump_memory : BOOL;
	level2 : INT := 0;
	level3 : INT := 0;
	pump3 : BOOL;
	a : INT;
	b : INT;
	c : BOOL;
	tube : BOOL;
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

a := level2;
b := level3;
c := pump3;

IF level2 >= 10 THEN 
	tube := TRUE;	
ELSIF level2 < 10 THEN
	tube := FALSE;
END_IF;