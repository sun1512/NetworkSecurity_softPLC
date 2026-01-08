PROGRAM PLC_PRG
  VAR
    level AT %QW0 : UINT;
    request AT %QX0.0 : BOOL := FALSE;
  END_VAR
  VAR
    open_req : BOOL;
    close_req : BOOL;
    low_2 : UINT := 10;
    high_2 : UINT := 20;
  END_VAR

  open_req := level <= low_2;
  close_req := level >=  high_2;
  request := NOT(close_req) AND (open_req OR request);
    
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#500ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : PLC_PRG;
  END_RESOURCE
END_CONFIGURATION

(* Codice da inserire nell'intefaccia web di openplc *)