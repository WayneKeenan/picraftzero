
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from signal import pause


from picraft.zero import MessageReceiver, Wheelbase, PanTilt, Joystick, filter_messages, \
    steering_mixer, pantilt_converter, join_values, SourcePrinter, scaled_pair, custom_source_tool, start


# Create a 'message receiver'  (Defaults to receiving messages via a WebSocket server)
# This also starts an embedded HTTP server for delivering content, e.g. HTML/JS joysticks.
# The (WebSocket) Messages are a simple dictionary with keys of:
#   'type'  => message type, e.g. 'JOYSTICK'
#   'id'    => a logical numeric identifier, e.g. 0 = 1st (or right hand side) joystick, 1 = 2nd etc....
#   'data'  => an array so it can easily be used as a tuple for later source/value processing

#messages = MessageReceiver()

# Find joysticks/thumbsticks for speed controll and pan/tilt control
# First parameter is a logical id where 0 = right stick, 1 = left stick
# Defaults to joysticks/thumbpads on the first connected controller found
joystick_right= Joystick(0)
joystick_left = Joystick(1)

#joystick_messages = MessageEmitter(messages, type='JOYSTICK', id=0)

wheelbase = Wheelbase(left=0, right=1)  # left/right: logical id of i2c motor (auto-detected Explorer pHAT or PiConZero)
pan_tilt = PanTilt(pan=0, tilt=1)       # pan/tilt  : logical id of i2c servo (auto-detected PanTilt HAT or PiConZero)

# The demo Web app has 2 virtual joysticks (id's 0 & 1) that support mouse (desktop) & touch (mobile)


# Joystick axis values are  (left/down)  -100 .. 100   (right/up)

# testing

printer = SourcePrinter()
printer2 = SourcePrinter()



def print_local_joystick():
    printer.name = "print_local_joystick"
    printer.source = joystick_right.values


def print_remote_joystick(joystick_id = 0):
    printer.name = "print_remote_joystick"
    printer.source = filter_messages(messages.values, type='JOYSTICK', id=joystick_id)


def print_combined_joysticks(joystick_id = 0):
    printer.name = "print_combined_joysticks"
    printer.source = join_values(filter_messages(messages.values, type='JOYSTICK', id=joystick_id),  joystick_right.values)


def print_local_joystick_scaled():
    printer.name = "print_local_joystick_scaled"
    printer.source = scaled_pair(joystick_right.values, 180, 0, -100, 100)



def print_local_joystick_mixed():
    printer.name = "print_local_joystick_mixed"
    printer.source = steering_mixer(joystick_right.values)


def print_local_joysticks():
    printer.name = "joystick_right.values"
    printer.source = joystick_right.values

    printer2.name = "joystick_left.values"
    printer2.source = joystick_left.values




def my_steering_mixer(yaw, throttle):
    max_power = 100
    yaw = yaw if yaw else 0
    throttle = throttle if throttle else 0
    left = throttle + yaw
    right = throttle - yaw
    scale = float(max_power) / max(1, abs(left), abs(right))
    # must return a 2 element tuple
    return int(left * scale), int(right * scale)

def print_local_joystick_custom_steering_mixer():
    printer.name = "print_local_joystick_custom_steering_mixer"
    printer.source = custom_source_tool(my_steering_mixer, joystick_right.values)



def print_pantilt_three_combined_streams():
    # Map input values from local and remote joysticks (scaled)
    # Accepts remote 'PANTILT' messages that  (scaling not required)
    printer.name = "print_pantilt_three_combined_streams"
    printer.source = join_values(
        scaled_pair(joystick_left.values, 0, 180, -100, 100),
        scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), 0, 180, -100, 100),
        filter_messages(messages.values, type='PANTILT', id=0)
    )



def triple_input_filter():
    printer.name = "triple_input_filter"

    printer.source = join_values(
        joystick_left.values,
        filter_messages(messages.values, type='JOYSTICK', id=1),
        filter_messages(messages.values, type='PANTILT', id=0),
    )

def triple_input_filter_all_input_scaled():
    printer.name = "triple_input_filter_all_input_scaled"

    printer.source = join_values(
        scaled_pair(joystick_left.values, -10, 10, -100, 100),
        scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=0), -50, 50, -100, 100),
        scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), -10, 10, -100, 100),
    )


def triple_input_filter_all_input_scaled_pantilt_conversion():
    printer.name = "triple_input_filter_all_input_scaled_pantilt_conversion"

    printer.source = pantilt_converter(
        join_values(
            scaled_pair(joystick_left.values, -10, 10, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=0), -50, 50, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), -10, 10, -100, 100),
        )
    )



def dual_triple_input_filter_all_input_scaled_pantilt_conversion():
    printer.name = "dual_triple_input_filter_all_input_scaled_pantilt_conversion__ONE"

    printer.source = pantilt_converter(
        join_values(
            scaled_pair(joystick_left.values, -10, 10, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=0), -50, 50, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), -10, 10, -100, 100),
        )
    )

    printer2.name = "dual_triple_input_filter_all_input_scaled_pantilt_conversion__TWO"
    printer2.source = pantilt_converter(
        join_values(
            scaled_pair(joystick_left.values, -10, 10, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=0), -50, 50, -100, 100),
            scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), -10, 10, -100, 100),
        )
    )

# ---
# HArdware interation tests

def local_joystick_wheelbase():
    wheelbase.source = steering_mixer(joystick_right.values)
    #wheelbase.source = joystick_right.values

def local_joystick_pantilt():
    pan_tilt.source = pantilt_converter(joystick_left.values)


def remote_joystick_wheelbase():
    wheelbase.source = steering_mixer(filter_messages(messages.values, type='JOYSTICK', id=0) )

def remote_joystick_pantilt():
    pan_tilt.source = pantilt_converter(filter_messages(messages.values, type='JOYSTICK', id=1))




def local_joystick_wheelbase_pantilt():
    wheelbase.source = steering_mixer(joystick_right.values)
    pan_tilt.source = pantilt_converter(joystick_left.values)


def dual_joystick_wheelbase():
    wheelbase.source = join_values(
        joystick_right.values,
        filter_messages(messages.values, type='JOYSTICK', id=0),
    )

def dual_joystick_pantilt():

    pan_tilt.source = join_values(
        joystick_left.values,
        filter_messages(messages.values, type='JOYSTICK', id=1),
    )


def dual_joystick_wheelbase_pantilt():
    wheelbase.source = join_values(
        joystick_right.values,
        filter_messages(messages.values, type='JOYSTICK', id=0),
    )

    pan_tilt.source = join_values(
        joystick_left.values,
        filter_messages(messages.values, type='JOYSTICK', id=1),
    )



def triple_input_pantilt_no_scaling_no_conversion():
    pan_tilt.source = join_values(
        joystick_left.values,
        filter_messages(messages.values, type='JOYSTICK', id=1),
        filter_messages(messages.values, type='PANTILT', id=0),
    )


def triple_input_pantilt_scaling_no_conversion():

    pan_tilt.source = join_values(
        filter_messages(messages.values, type='JOYSTICK', id=1),
        filter_messages(messages.values, type='PANTILT', id=0),
        scaled_pair(joystick_left.values, 0, 180, -100, 100),
    )


# Mock Robots



def mock_robot_builtin_pantilt_conversion():
    printer.name = "mock_robot_builtin_pantilt_conversion___WHEELS"

    printer.source = steering_mixer(
        join_values(
            filter_messages(messages.values, type='JOYSTICK', id=0),
            joystick_right.values
        )
    )

    printer2.name = "mock_robot_builtin_pantilt_conversion__PANTILT"

    printer2.source = join_values(
        filter_messages(messages.values, type='PANTILT', id=0),
        pantilt_converter(
            join_values(
                scaled_pair(joystick_left.values, -10, 10, -100, 100),
                filter_messages(messages.values, type='JOYSTICK', id=1),
            )
        )
    )

def mock_robot():
    printer.name = "mock_robot___WHEELS"

    printer.source = steering_mixer(
        join_values(
            filter_messages(messages.values, type='JOYSTICK', id=0),
            joystick_right.values
        )
    )

    printer2.name = "mock_robot__PANTILT"

    printer2.source = join_values(
        filter_messages(messages.values, type='PANTILT', id=0),
        scaled_pair(
            join_values(joystick_left.values, filter_messages(messages.values, type='JOYSTICK', id=1)), 180, 0, -100, 100),
        )






# ------------------------------------------------
# Robots





def simple_robot_local_joystick():
    wheelbase.source = steering_mixer(joystick_right.values)
    pan_tilt.source  = pantilt_converter(joystick_left.values)


def simple_robot_dual_joystick():
    wheelbase.source = steering_mixer(join_values(
        joystick_right.values,
        filter_messages(messages.values, type='JOYSTICK', id=0))
    )
    pan_tilt.source  = pantilt_converter(join_values(
        joystick_left.values,
        filter_messages(messages.values, type='JOYSTICK', id=1)))




def robot():
    wheelbase.source = steering_mixer(
        join_values(
            filter_messages(messages.values, type='JOYSTICK', id=0),
            joystick_right.values
        )
    )

    pan_tilt.source = join_values(
        filter_messages(messages.values, type='PANTILT', id=0),
        scaled_pair(
            join_values(joystick_left.values, filter_messages(messages.values, type='JOYSTICK', id=1)), 180, 0, -100, 100),
        # filter_messages(messages.values, type='PANTILT', id=0),
        # scaled_pair(joystick_left.values, 0, 180, -100, 100),
        # scaled_pair(filter_messages(messages.values, type='JOYSTICK', id=1), 0, 180, -100, 100),
    )





# ---
# Start the music, light the lights...


#triple_input_filter()
#triple_input_filter_all_input_scaled()
#triple_input_filter_all_input_scaled_pantilt_conversion()
#dual_triple_input_filter_all_input_scaled_pantilt_conversion()


#print_local_joystick()
#print_local_joysticks()
#print_remote_joystick()
#print_combined_joysticks()
#print_local_joystick_scaled()
#print_local_joystick_mixed()
#print_local_joystick_custom_steering_mixer()



local_joystick_wheelbase()
#local_joystick_pantilt()
#local_joystick_wheelbase_pantilt()

#remote_joystick_wheelbase()
#remote_joystick_pantilt()

#dual_joystick_wheelbase()
#dual_joystick_pantilt()
#dual_joystick_wheelbase_pantilt()

#simple_robot_local_joystick()
#simple_robot_dual_joystick()

#triple_input_pantilt_no_scaling_no_conversion()
#triple_input_pantilt_scaling_no_conversion()


#mock_robot_builtin_pantilt_conversion()
#mock_robot()

#robot()


# Slow things down for testing:
wheelbase.source_delay = 1
#pan_tilt.source_delay = 1
printer.source_delay = 1
printer2.source_delay = 1

start()

