PROGRAM PLC_PRG
VAR
    level : INT;
    pump : BOOL;
    low : BOOL;
    high : BOOL;
    low_3 : INT := 0;
    high_3 : INT := 3;
END_VAR


low := level <=  low_3;
high := level >= high_3;
pump := NOT(low) AND (high OR pump);
  