-- MAIN PROGRAM
props=require("propcase")

function timestamp()
 Y=get_time("Y")
 M=get_time("M")
 D=get_time("D")
 h=get_time("h")
 m=get_time("m")
 s=get_time("s")
 return ( Y .. "-" .. M .. "-" .. D .. " " .. h .. ":" .. m .. ":" .. s)
end

function writelog(msg)
 ts=timestamp()
 
 t0=get_temperature(0)
 t1=get_temperature(1)
 t2=get_temperature(2)
 orient=get_prop(219)
 volt=get_vbatt() 
 
 print_screen(-1 * D) --negative means append (in case of a restart, we dont want to overwrite)
 
 -- time, temp1, temp2, temp3, orientation, battery voltage, message
 print('' .. ts .. ',' .. t0 .. ',' .. t1 .. ',' .. t2 .. ',' .. orient .. ',' .. volt .. ',' .. msg)
end





--- main execution starts here
print_screen(1)
print("mission started")

-- log file number by day of month

D=get_time("D")
print_screen(-1 * D) --negative means append (in case of a restart, we dont want to overwrite)

-- write log header
print("time, temp1, temp2, temp3, orientation, voltage, message")


-- flash off
set_prop(143,2)

-- set 100 ISO
set_prop(149,200)
 
-- set picture size to L (max)
set_prop(220,0)
 
-- set quality to Superfine
set_prop(57,0)

-- lock 
set_aflock(1)

-- set focus mode to manual/infinity
set_prop(133,1)
set_prop(6,3)
set_prop(65,-1)

sleep(5000)

writelog("init")

cnt = 0
while true do
  if cnt%5 == 0 then
  	writelog("INFO")
  end
  shoot()
  sleep(1500)
  shoot()

  -- display off
  set_lcd_display(0)
  sleep(60000)
  cnt = cnt + 1

end
             

