--[[
Authors: Fraser McCrossan
         Alfredo Pironti
	 Torben S.
Tested on G9, A2000, should work on most cameras.

An accurate intervalometer script, with pre-focus and screen power off options.
http://chdk.wikia.com/wiki/Lua/Scripts:_Accurate_Intervalometer_with_power-saving_and_pre-focus

Added on Dec 22, 2013:  Fixed display off functionality to use the recently added set_lcd_display CHDK function

Features:
 - input is frame interval plus total desired run-time (or "endless")
 - displays frame count, frame total and remaining time after each frame
   (in endless mode, displays frame count and elapsed time)
 - honours the "Display" button during frame delays (so you can
   get it running then turn off the display to save power)
 - can turn off the display a given number of frames after starting
   (might take a couple of frames longer to cycle to correct mode)
 - can pre-focus before starting then go to manual focus mode
 - use SET button to exit 

 See bottom of script for main loop.
]]

--[[
@title Time-lapse
@param s Secs/frame
@default s 30
@param h Sequence hours
@default h 0
@param m Sequence minutes
@default m 0
@param e Endless?
@default e 1
@range e 0 1
@param f Fix focus at start?
@default f 0
@range f 0 1
@param d Display off frame 0=never
@default d 3
@param r Refocus until frame 0=never
@default r 40
@range r 0 50

--]]

-- convert parameters into readable variable names
secs_frame, hours, minutes, endless, focus_at_start, display_off_frame = s, h, m, (e == 1), (f == 1), d, refocus_until 

-- sanitize parameters
if secs_frame <= 0 then
	secs_frame = 1
end
if hours < 0 then
	hours = 0
end
if minutes <= 0 then
	minutes = 1
end
if display_off_frame < 0 then
	display_off_frame = 0
end

props = require "propcase"

-- derive actual running parameters from the more human-friendly input
-- parameters
function calculate_parameters (seconds_per_frame, hours, minutes)
   local ticks_per_frame = 1000 * secs_frame -- ticks per frame
   local total_frames = (((hours * 3600 + minutes * 60) - 1) / secs_frame) + 1 -- total frames
   return ticks_per_frame, total_frames
end

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
 D=get_time("D")
 
 t0=get_temperature(0)
 t1=get_temperature(1)
 t2=get_temperature(2)
 orient=get_prop(219)
 volt=get_vbatt() 
 
 print_screen(-1 * D) --negative means append (in case of a restart, we dont want to overwrite)
 
 -- time, temp1, temp2, temp3, orientation, battery voltage, message
 print('' .. ts .. ',' .. t0 .. ',' .. t1 .. ',' .. t2 .. ',' .. orient .. ',' .. volt .. ',' .. msg)
end




function print_status (frame, total_frames, ticks_per_frame, endless, free)
   if endless then
      local h, m, s = ticks_to_hms(frame * ticks_per_frame)
      print("#" .. frame .. ", " .. h .. "h " .. m .. "m " .. s .. "s")
   else
      if frame < total_frames then
      	  local h, m, s = ticks_to_hms(ticks_per_frame * (total_frames - frame))
	      print(frame .. "/" .. total_frames .. ", " .. h .. "h" .. m .. "m" .. s .. "s/" .. free .. " left")
	  else
	  	  print(frame .. "/" .. total_frames .. ", " .. free .. " left")
	  end
   end
end

function ticks_to_hms (ticks)
   local secs = (ticks + 500) / 1000 -- round to nearest seconds
   local s = secs % 60
   secs = secs / 60
   local m = secs % 60
   local h = secs / 60
   return h, m, s
end

-- sleep, but using wait_click(); return true if a key was pressed, else false
function next_frame_sleep (frame, start_ticks, ticks_per_frame, total_frames)
   -- this calculates the number of ticks between now and the time of
   -- the next frame
	if frame == total_frames then
   		return false
    end
   local next_frame = start_ticks + frame * ticks_per_frame
   local sleep_time = next_frame - get_tick_count()
   if sleep_time < 1 then
      sleep_time = 1
   end
   wait_click(sleep_time)
   return not is_key("no_key")
end

-- delay for the appropriate amount of time, but respond to
-- the display key (allows turning off display to save power)
-- return true if we should exit, else false
function frame_delay (frame, start_ticks, ticks_per_frame, total_frames)
   -- this returns true while a key has been pressed, and false if
   -- none
   while next_frame_sleep (frame, start_ticks, ticks_per_frame, total_frames) do
      -- honour the display button
      if is_key("display") then
-- vvvvvvv  CHANGED  vvvvvvv
--	 click("display")
		set_lcd_display(1)
		display_off_frame = frame + display_off_frame
-- ^^^^^^^  CHANGED  ^^^^^^^
      end
      -- if set key is pressed, indicate that we should stop
      if is_key("set") then
-- vvvvvvv  ADDED  vvvvvvv
	 set_lcd_display(1)
-- ^^^^^^^  ADDED  ^^^^^^^
	 return true
      end
   end
   return false
end

-- if the display mode is not the passed mode, click display and return true
-- otherwise return false
-- vvvvvvv  REMOVED  vvvvvvv
--function seek_display_mode(mode)
--   if get_prop(props.DISPLAY_MODE) == mode then
--      return false
--   else
--      click "display"
--      return true
--   end
--end
-- ^^^^^^^  REMOVED  ^^^^^^^

-- wait for "name" button click until timeout.
-- returns true if button was clicked, false if timeout expired
function wait_button(timeout, name)
	if timeout < 1 then
		return false
	end
	local cur_timeout = timeout
	local start_time = get_tick_count()
	while cur_timeout > 0 do
		wait_click(cur_timeout)
		if is_key("no_key") then
			-- timeout expired
			return false
		else
			if is_key(name) then
				-- user clicked requested key
				return true
			end
		end
		-- user clicked an unwanted key, we continue sleeping
		local now = get_tick_count()
		local elapsed = now - start_time
		start_time = now
		cur_timeout = cur_timeout - elapsed
	end
	return false
end

-- switch to autofocus mode, pre-focus, then go to manual focus mode
function pre_focus()
   set_aflock(0)
   local try = 1
   while try <= 5 do
      print("Pre-focus attempt " .. try)
      press("shoot_half")
      sleep(2000)
      if get_focus_state() > 0 then
		 set_aflock(1)
		 return get_focus()
      end
      release("shoot_half")
      sleep(500)
      try = try + 1
   end
   return -1
end

-- vvvvvvv  CHANGED  vvvvvvv
function restore()
-- restore focus mode
set_aflock(0)
set_lcd_display(1)
end
-- ^^^^^^^  CHANGED  ^^^^^^^

print "Starting in 60 seconds"
sleep(60000)

if focus_at_start then
	local got_focus = pre_focus()
   if got_focus < 0 then
      print "Unable to reach pre-focus"
      print("Starting to shoot in 1 second")
	  sleep(1000)
   else
   	  local refocus = true
   	  while refocus do
		  print("Press SET to focus again")
		  print("or shooting will start in 1 second")
		  refocus = wait_button(1000,"set")
		  release("shoot_half")
		  if refocus then
		  	got_focus = pre_focus()
		  	if got_focus < 0 then
		  		refocus = false
		  		print "Unable to reach pre-focus"
		  		print("Starting to shoot in 1 second")
				sleep(1000)
		  	end
		  end
	  end      
   end
else
	print("Starting to shoot in 1 second")
	sleep(1000)
end

ticks_per_frame, total_frames = calculate_parameters(secs_frame, hours, minutes)

frame = 1
-- vvvvvvv  REMOVED  vvvvvvv
-- original_display_mode = get_prop(props.DISPLAY_MODE)
-- target_display_mode = 2 -- off
-- ^^^^^^^  REMOVED  ^^^^^^^



-- flash off
set_prop(143,2)

-- set 100 ISO
--set_prop(149,200)
 
-- set picture size to L (max)
set_prop(220,0)
 
-- set quality to Superfine
set_prop(57,0)

print "Starting - Press SET to exit"

start_ticks = get_tick_count()


while endless or frame <= total_frames do
   local free = get_jpg_count() - 1 -- to account for the one we're going to make
   -- in CHDK 1.2 we could check the return value of shoot()
   -- but get_jpg_count() gives more compatibility
   if free < 0 then
   	print "Memory full"
   	break
   end
   print_status(frame, total_frames, ticks_per_frame, endless, free)
-- vvvvvvv  CHANGED  vvvvvvv
   if display_off_frame > 0 and frame > display_off_frame then
      -- seek_display_mode(target_display_mode)
	  set_lcd_display(0)
-- ^^^^^^^  CHANGED  ^^^^^^^
   end
   shoot()
   if frame_delay(frame, start_ticks, ticks_per_frame, total_frames) then
      print "User quit"
      break
   end
   frame = frame + 1
   if frame % 10 == 0 then --and refocus_until >= frame then
   	local got_focus = pre_focus()
   end
end

restore()
