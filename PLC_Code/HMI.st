PROGRAM HMI
  VAR
    level_1 AT %QW0 : INT := 45;
    level_2 AT %QW1 : INT := 0;
    level_3 AT %QW2 : INT := 0;
    pump_1 AT %QX0.0 : BOOL;
    valve AT %QX0.1 : BOOL;
    pump_3 AT %QX0.2 : BOOL;
  END_VAR
  VAR
    tubeOUT_2 : BOOL;
  END_VAR

  IF level_2 >= 10 THEN
    tubeOUT_2 := TRUE;
  ELSIF level_2 < 10 THEN
    tubeOUT_2 := FALSE;
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : HMI;
  END_RESOURCE
END_CONFIGURATION

(* Codice da inserire nell'intefaccia web di openplc *)
