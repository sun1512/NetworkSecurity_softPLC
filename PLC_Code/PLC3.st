PROGRAM MAIN
VAR
    level : WORD;
    pump : BOOL;
    low : BOOL;
    high : BOOL;
    low_3 : INT := 0;
    high_3 : INT := 3;
END_VAR


level := GVL.mb_Output_Registers[0];

low := level <=  low_3;
high := level >= high_3;
pump := NOT(low) AND (high OR pump);

GVL.mb_Input_Coils[0] := pump;
  