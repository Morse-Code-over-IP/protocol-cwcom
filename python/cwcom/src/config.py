"""
MIT License

Copyright (c) 2020 PyKOB - MorseKOB in Python

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""config module

Reads configuration information for `per-machine` and `per-user` values.

An example of a `per-machine` value is the KOB serial/com port (PORT).
An example of a `per-user` value is the code speed (WPM).

Configuration/preference values are read/written to:
 Windows:
  User: [user]\AppData\Roaming\pykob\config-[user].ini
  Machine: \ProgramData\pykob\config_app.ini
 Mac:
  User: ~/.pykob/config-[user].ini
  Machine: ~/.pykob/config_app.ini
 Linux:
  User: ~/.pykob/config-[user].ini
  Machine: ~/.pykob/config_app.ini

The files are INI format with the values in a section named "PYKOB".

"""
import argparse
import configparser
import distutils
import getpass
import os
import platform
import pykob
import socket
import sys
from distutils.util import strtobool
from enum import Enum, IntEnum, unique
from pykob import log

@unique
class Spacing(IntEnum):
    none = 0
    char = 1
    word = 2

@unique
class CodeType(IntEnum):
    american = 1
    international = 2

@unique
class InterfaceType(IntEnum):
    key_sounder = 1
    loop = 2
    keyer = 3

# Application name
__APP_NAME = "pykob"
# INI Section
__CONFIG_SECTION = "PYKOB"
# System/Machine INI file Parameters/Keys
__SERIAL_PORT_KEY = "PORT"
__GPIO_KEY = "GPIO"
# User INI file Parameters/Keys
__AUTO_CONNECT_KEY = "AUTO_CONNECT"
__CODE_TYPE_KEY = "CODE_TYPE"
__INTERFACE_TYPE_KEY = "INTERFACE_TYPE"
__INVERT_KEY_INPUT_KEY = "KEY_INPUT_INVERT"
__LOCAL_KEY = "LOCAL"
__MIN_CHAR_SPEED_KEY = "CHAR_SPEED_MIN"
__REMOTE_KEY = "REMOTE"
__SERVER_URL_KEY = "SERVER_URL"
__SOUND_KEY = "SOUND"
__SOUNDER_KEY = "SOUNDER"
__SOUNDER_POWER_SAVE_KEY = "SOUNDER_POWER_SAVE"
__SPACING_KEY = "SPACING"
__STATION_KEY = "STATION"
__TEXT_SPEED_KEY = "TEXT_SPEED"
__WIRE_KEY = "WIRE"


# Paths and Configurations
app_config_dir = None
app_config_file_path = None
app_config = None
user_config_dir = None
user_config_file_path = None
user_config = None

# System information
hostname = None
os_name = None
platform_name = None
pyaudio_version = None
pyserial_version = None
python_version = None
pykob_version = None
system_name = None
system_version = None
user_home = None
user_name = None

# Machine/System Settings
serial_port = None
gpio = False

# User Settings
auto_connect = False
code_type = CodeType.american
interface_type = InterfaceType.loop
invert_key_input = False
local = True
remote = True
server_url = None
sound = True
sounder = False
spacing = Spacing.none
station = None
wire = 0
min_char_speed = 18
text_speed = 18

def onOffFromBool(b):
    """Return 'ON' if `b` is `True` and 'OFF' if `b` is `False`

    Parameters
    ----------
    b : boolean
        The value to evaluate
    Return
    ------
        'ON' for `True`, 'OFF' for `False`
    """
    #print(b)
    r = "ON" if b else "OFF"
    return r

def noneOrValueFromStr(s):
    """Return `None` if `s` is '' and the string value otherwise

    Parameters
    ----------
    s : str
        The string value to evaluate
    Return
    ------
        `None` or the string value
"""
    r = None if not s or not s.strip() or s.upper() == 'NONE' else s
    return r

def create_config_files_if_needed():
    global app_config_dir
    global app_config_file_path
    global user_config_dir
    global user_config_file_path

    # Create the files if they don't exist
    if not os.path.isfile(user_config_file_path):
        # need to create
        user_config_dir = os.path.split(user_config_file_path)[0]
        if not os.path.isdir(user_config_dir):
            os.makedirs(user_config_dir)
        f = open(user_config_file_path, 'w')
        f.close()
    if not os.path.isfile(app_config_file_path):
        # need to create
        app_config_dir = os.path.split(app_config_file_path)[0]
        if not os.path.isdir(app_config_dir):
            os.makedirs(app_config_dir)
        f = open(app_config_file_path, 'w')
        f.close()

def set_auto_connect(s):
    """Sets the Auto Connect to wire enable state

    When set to `True` via a value of "TRUE"/"ON"/"YES" the application should 
    automatically connect to the configured wire.

    Note that this is a 'suggestion'. It isn't used by the base pykob 
    modules. It should be used by applications (like MKOB) to initiate a connection 
    to the configured wire.
    
    Parameters
    ----------
    s : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE` 
        will enable auto-connect. Values of `NO`|`OFF`|`FALSE` will disable auto-connect.
    """

    global auto_connect
    try:
        auto_connect = strtobool(str(s))
        user_config.set(__CONFIG_SECTION, __AUTO_CONNECT_KEY, onOffFromBool(auto_connect))
    except ValueError as ex:
        log.err("Auto Connect value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_code_type(s):
    """Sets the Code Type (for American or International)

    Parameters
    ----------
    s : str
        The value `A|AMERICAN` will set the code type to 'American'.
        The value `I|INTERNATIONAL` will set the code type to 'International'.
    """

    global code_type
    s = s.upper()
    if s=="A" or s=="AMERICAN":
        code_type = CodeType.american
    elif s=="I" or s=="INTERNATIONAL":
        code_type = CodeType.international
    else:
        msg = "TYPE value '{}' is not a valid `Code Type` value of 'AMERICAN' or 'INTERNATIONAL'.".format(s)
        log.err(msg)
        raise ValueError(msg)
    user_config.set(__CONFIG_SECTION, __CODE_TYPE_KEY, code_type.name.upper())


def set_interface_type(s):
    """Sets the Interface Type (for Key-Sounder, Loop or Keyer)

    Parameters
    ----------
    s : str
        The value `KS|KEY_SOUNDER` will set the interface type to 'InterfaceType.key_sounder'.
        The value `L|LOOP` will set the interface type to 'InterfaceType.loop'.
        The value `K|KEYER` will set the interface type to 'InterfaceType.keyer'.
    """

    global interface_type
    s = s.upper()
    if s=="KS" or s=="KEY_SOUNDER":
        interface_type = InterfaceType.key_sounder
    elif s=="L" or s=="LOOP":
        interface_type = InterfaceType.loop
    elif s=="K" or s=="KEYER":
        interface_type = InterfaceType.keyer
    else:
        msg = "TYPE value '{}' is not a valid `Interface Type` value of 'KEY_SOUNDER', 'LOOP' or 'KEYER'.".format(s)
        log.err(msg)
        raise ValueError(msg)
    user_config.set(__CONFIG_SECTION, __INTERFACE_TYPE_KEY, interface_type.name.upper())


def set_invert_key_input(b):
    """
    Enable/disable key input signal (DSR) invert.

    When key-invert is enabled, the key input (DSR on the serial interface)
    is inverted (because the RS-232 logic is inverted). This is primarily used
    when the input is from a modem (in dial-up connection).

    Parameters
    ----------
    b : string 'true/false'
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE`
        will enable key invert. Values of `NO`|`OFF`|`FALSE` will disable key invert.
    """
    global invert_key_input
    try:
        invert_key_input = strtobool(str(b))
        user_config.set(__CONFIG_SECTION, __INVERT_KEY_INPUT_KEY, onOffFromBool(invert_key_input))
    except ValueError as ex:
        log.err("INVERT KEY INPUT value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_local(l):
    """Enable/disable local copy

    When local copy is enabled, the local sound/sounder configuration is
    used to locally sound the content being sent to the wire.

    Parameters
    ----------
    l : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE`
        will enable local copy. Values of `NO`|`OFF`|`FALSE` will disable local copy.
    """

    global local
    try:
        local = strtobool(str(l))
        user_config.set(__CONFIG_SECTION, __LOCAL_KEY, onOffFromBool(local))
    except ValueError as ex:
        log.err("LOCAL value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_remote(r):
    """Enable/disable remote send

    When remote send is enabled, the content will be sent to the
    wire configured.

    Parameters
    ----------
    r : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE`
        will enable remote send. Values of `NO`|`OFF`|`FALSE` will disable remote send.
    """

    global remote
    try:
        remote = strtobool(str(r))
        user_config.set(__CONFIG_SECTION, __REMOTE_KEY, onOffFromBool(remote))
    except ValueError as ex:
        log.err("REMOTE value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_min_char_speed(s):
    """Sets the minimum character speed in words per minute

    A difference between character speed (in WPM) and text speed
    (in WPM) is used to calulate a Farnsworth timing value.

    This is the minimum character speed. If the text speed is
    higher, then the character speed will be bumped up to
    the text speed.

    Parameters
    ----------
    s : str
        The speed in words-per-minute as an interger string value
    """

    global min_char_speed
    try:
        _speed = int(s)
        min_char_speed = _speed
        user_config.set(__CONFIG_SECTION, __MIN_CHAR_SPEED_KEY, str(min_char_speed))
    except ValueError as ex:
        log.err("CHARS value '{}' is not a valid integer value. Not setting CWPM value.".format(ex.args[0]))
        raise

def set_serial_port(p):
    """Sets the name/path of the serial/tty port to use for a
    key+sounder/loop interface

    Parameters
    ----------
    p : str
        The 'COM' port for Windows, the 'tty' device path for Mac and Linux
    """

    global serial_port
    serial_port = noneOrValueFromStr(p)
    app_config.set(__CONFIG_SECTION, __SERIAL_PORT_KEY, serial_port)

def set_gpio(s):
    """Sets the key/sounder interface to Raspberry Pi GPIO

    When set to `True` via a value of "TRUE"/"ON"/"YES" the application should 
    enable the GPIO interface to the key/sounder.
    
    Parameters
    ----------
    s : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE` 
        will enable GPIO interface. Values of `NO`|`OFF`|`FALSE` will disable GPIO.
        Serial port will become active (if configured for sounder = ON)
    """

    global gpio
    try:
        gpio = strtobool(str(s))
        app_config.set(__CONFIG_SECTION, __GPIO_KEY, onOffFromBool(gpio))
    except ValueError as ex:
        log.err("GPIO value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_server_url(s):
    """Sets the KOB Server URL to connect to for wires

    Parameters
    ----------
    s : str
        The KOB Server URL or None. Also set to None if the value is 'DEFAULT'.
    """

    global server_url
    server_url = noneOrValueFromStr(s)
    if server_url and server_url.upper() == 'DEFAULT':
        server_url = None
    user_config.set(__CONFIG_SECTION, __SERVER_URL_KEY, server_url)

def set_sound(s):
    """Sets the Sound/Audio enable state

    When set to `True` via a value of "TRUE"/"ON"/"YES" the computer audio
    will be used to produce sounder output.

    Parameters
    ----------
    s : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE`
        will enable sound. Values of `NO`|`OFF`|`FALSE` will disable sound.
    """

    global sound
    try:
        sound = strtobool(str(s))
        user_config.set(__CONFIG_SECTION, __SOUND_KEY, onOffFromBool(sound))
    except ValueError as ex:
        log.err("SOUND value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_sounder(s):
    """Sets the Sounder enable state

    When set to `True` via a value of "TRUE"/"ON"/"YES" the sounder will
    be driven if the `port` value is configured.

    Parameters
    ----------
    s : str
        The enable/disable state to set as a string. Values of `YES`|`ON`|`TRUE`
        will enable sounder output. Values of `NO`|`OFF`|`FALSE` will disable
        sounder output.
    """

    global sounder
    try:
        sounder = strtobool(str(s))
        user_config.set(__CONFIG_SECTION, __SOUNDER_KEY, onOffFromBool(sounder))
    except ValueError as ex:
        log.err("SOUNDER value '{}' is not a valid boolean value. Not setting value.".format(ex.args[0]))
        raise

def set_sounder_power_save(s):
    """Sets the time (in seconds) to delay before de-energizing the sounder to save power

    To save power, reduce fire risk, etc. the sounder drive circuit will be de-energized after
    this many seconds of idle time. Setting this to zero (0) will disable the power save functionality.

    Parameters
    ----------
    s : str
        The number of idle seconds before power-save as an interger string value
    """

    global sounder_power_save
    try:
        _seconds = int(s)
        sounder_power_save = _seconds if _seconds >= 0 else 0
        user_config.set(__CONFIG_SECTION, __SOUNDER_POWER_SAVE_KEY, str(sounder_power_save))
    except ValueError as ex:
        log.err("Idle time '{}' is not a valid integer value. Not setting SounderPowerSave value.".format(ex.args[0]))
        raise

def set_spacing(s):
    """Sets the Spacing (for Farnsworth timing) to None (disabled) `Spacing.none`,
    Character `Spacing.char` or Word `Spacing.word`

    When set to `Spacing.none` Farnsworth spacing will not be added.
    When set to `Spacing.char` Farnsworth spacing will be added between characters.
    When set to `Spacing.word` Farnsworth spacing will be added between words.

    Parameters
    ----------
    s : str
        The value `N|NONE` will set the spacing to `Spacing.none` (disabled).
        The value `C|CHAR` will set the spacing to `Spacing.char`.
        The value `W|WORD` will set the spacing to `Spacing.word`.
    """

    global spacing
    s = s.upper()
    if s=="N" or s=="NONE":
        spacing = Spacing.none
    elif s=="C" or s=="CHAR" or s=="CHARACTER":
        spacing = Spacing.char
    elif s=="W" or s=="WORD":
        spacing = Spacing.word
    else:
        msg = "SPACING value '{}' is not a valid `Spacing` value of 'NONE', 'CHAR' or 'WORD'.".format(s)
        log.err(msg)
        raise ValueError(msg)
    user_config.set(__CONFIG_SECTION, __SPACING_KEY, spacing.name.upper())


def set_station(s):
    """Sets the Station ID to use when connecting to a wire

    Parameters
    ----------
    s : str
        The Station ID
    """

    global station
    station = noneOrValueFromStr(s)
    user_config.set(__CONFIG_SECTION, __STATION_KEY, station)

def set_wire(w: str):
    """Sets the wire to connect to

    Parameters
    ----------
    w : str
        The Wire number
    """

    global wire
    try:
        _wire = int(w)
        wire = _wire
        user_config.set(__CONFIG_SECTION, __WIRE_KEY, str(wire))
    except ValueError as ex:
        log.err("Wire number value '{}' is not a valid integer value.".format(ex.args[0]))
        raise

def set_text_speed(s):
    """Sets the Text (code) speed in words per minute

    Parameters
    ----------
    s : str
        The text speed in words-per-minute as an interger string value
    """

    global text_speed
    try:
        _speed = int(s)
        text_speed = _speed
        user_config.set(__CONFIG_SECTION, __TEXT_SPEED_KEY, str(text_speed))
    except ValueError as ex:
        log.err("Text speed value '{}' is not a valid integer value.".format(ex.args[0]))
        raise

def print_info():
    """Print system and PyKOB configuration information
    """

    print_system_info()
    print_config()

def print_system_info():
    """Print system information
    """

    print("User:", user_name)
    print("User Home Path:", user_home)
    print("User Configuration File:", user_config_file_path)
    print("App Configuration File", app_config_file_path)
    print("OS:", os_name)
    print("System:", system_name)
    print("Version:", system_version)
    print("Platform:", platform_name)
    print("PyKOB:", pykob_version)
    print("Python:", python_version)
    print("PyAudio:", pyaudio_version)
    print("PySerial:", pyserial_version)
    print("Host:", hostname)

def print_config():
    """Print the PyKOB configuration
    """
    url = noneOrValueFromStr(server_url)
    url = url if url else ''
    print("======================================")
    print("Serial serial_port: '{}'".format(serial_port))
    print("GPIO interface (Raspberry Pi):", onOffFromBool(gpio))
    print("--------------------------------------")
    print("Auto Connect to Wire:", onOffFromBool(auto_connect))
    print("Code type:", code_type.name.upper())
    print("Interface type:", interface_type.name.upper())
    print("Invert key input:", onOffFromBool(invert_key_input))
    print("Local copy:", onOffFromBool(local))
    print("Remote send:", onOffFromBool(remote))
    print("KOB Server URL:", url)
    print("Sound:", onOffFromBool(sound))
    print("Sounder:", onOffFromBool(sounder))
    print("Sounder Power Save (seconds):", sounder_power_save)
    print("Spacing:", spacing.name.upper())
    print("Station: '{}'".format(noneOrValueFromStr(station)))
    print("Wire:", wire)
    print("Character speed", min_char_speed)
    print("Words per min speed:", text_speed)

def save_config():
    """Save (write) the configuration values out to the user and
    system/machine config files.
    """

    create_config_files_if_needed()
    with open(user_config_file_path, 'w') as configfile:
        user_config.write(configfile, space_around_delimiters=False)
    with open(app_config_file_path, 'w') as configfile:
        app_config.write(configfile, space_around_delimiters=False)

def read_config():
    """Read the configuration values from the user and machine config files.
    """

    global hostname
    global platform_name
    global os_name
    global pykob_version
    global python_version
    global pyaudio_version
    global pyserial_version
    global system_name
    global system_version
    global app_config
    global app_config_file_path
    global user_config
    global user_config_file_path
    global user_home
    global user_name
    #
    global serial_port
    global gpio
    #
    global auto_connect
    global code_type
    global interface_type
    global invert_key_input
    global local
    global min_char_speed
    global remote
    global server_url
    global sound
    global sounder
    global sounder_power_save
    global spacing
    global station
    global wire
    global text_speed

    # Get the system data
    try:
        user_name = getpass.getuser()
        user_home = os.path.expanduser('~')
        os_name = os.name
        system_name = platform.system()
        system_version = platform.release()
        platform_name = sys.platform
        pykob_version = pykob.VERSION
        python_version = "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        try:
            import pyaudio
            pyaudio_version = pyaudio.__version__ # NOTE: Using '__" property - not recommended, but only way to get version
        except:
            pyaudio_version = "PyAudio is not installed or the version information is not available (check installation)"
        try:
            import serial
            pyserial_version = serial.VERSION
        except:
            pyserial_version = "PySerial is not installed or the version information is not available (check installation)"
        hostname = socket.gethostname()

        # User configuration file name
        userConfigFileName = "config-{}.ini".format(user_name)
        app_configFileName = "config_app.ini"

        # Create the user and application configuration paths
        if system_name == "Windows":
            user_config_file_path = os.path.join(os.environ["LOCALAPPDATA"], os.path.normcase(os.path.join(__APP_NAME, userConfigFileName)))
            app_config_file_path = os.path.join(os.environ["ProgramData"], os.path.normcase(os.path.join(__APP_NAME, app_configFileName)))
        elif system_name == "Linux" or system_name == "Darwin": # Linux or Mac
            user_config_file_path = os.path.join(user_home, os.path.normcase(os.path.join(".{}".format(__APP_NAME), userConfigFileName)))
            app_config_file_path = os.path.join(user_home, os.path.normcase(os.path.join(".{}".format(__APP_NAME), app_configFileName)))
        else:
            log.err("Unknown System name")
            exit

    except KeyError as ex:
        log.err("Key '{}' not found in environment.".format(ex.args[0]))
        exit

    create_config_files_if_needed()

    user_config_defaults = {\
        __AUTO_CONNECT_KEY:"OFF", \
        __CODE_TYPE_KEY:"AMERICAN", \
        __INTERFACE_TYPE_KEY:"LOOP", \
        __INVERT_KEY_INPUT_KEY:"OFF", \
        __LOCAL_KEY:"ON", \
        __MIN_CHAR_SPEED_KEY:"18", \
        __REMOTE_KEY:"ON", \
        __SERVER_URL_KEY:"NONE", \
        __SOUND_KEY:"ON", \
        __SOUNDER_KEY:"OFF", \
        __SOUNDER_POWER_SAVE_KEY:"60", \
        __SPACING_KEY:"NONE", \
        __STATION_KEY:"", \
        __WIRE_KEY:"", \
        __TEXT_SPEED_KEY:"18"}
    app_config_defaults = {"PORT":"", "GPIO":"OFF"}

    user_config = configparser.ConfigParser(defaults=user_config_defaults, allow_no_value=True, default_section=__CONFIG_SECTION)
    app_config = configparser.ConfigParser(defaults=app_config_defaults, allow_no_value=True, default_section=__CONFIG_SECTION)

    user_config.read(user_config_file_path)
    app_config.read(app_config_file_path)

    try:
        ###
        # Get the System (App) config values
        ###
        serial_port = app_config.get(__CONFIG_SECTION, __SERIAL_PORT_KEY)
        # If there isn't a PORT value set PORT to None
        if not serial_port:
            serial_port = None

        # GPIO (Raspberry Pi)
        __option = "GPIO interface"
        __key = __GPIO_KEY
        gpio = app_config.getboolean(__CONFIG_SECTION, __key)
  
        ###
        # Get the User config values
        ###
        __option = "Auto Connect to Wire"
        __key = __AUTO_CONNECT_KEY
        auto_connect = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Code type"
        __key = __CODE_TYPE_KEY
        _code_type = (user_config.get(__CONFIG_SECTION, __key)).upper()
        if  _code_type == "AMERICAN":
            code_type = CodeType.american
        elif _code_type == "INTERNATIONAL":
            code_type = CodeType.international
        else:
            raise ValueError(_code_type)
        __option = "Interface type"
        __key = __INTERFACE_TYPE_KEY
        _interface_type = (user_config.get(__CONFIG_SECTION, __key)).upper()
        if _interface_type == "KEY_SOUNDER":
            interface_type = InterfaceType.key_sounder
        elif _interface_type == "LOOP":
            interface_type = InterfaceType.loop
        elif _interface_type == "KEYER":
            interface_type = InterfaceType.keyer
        else:
            raise ValueError(_interface_type)
        __option = "Invert key input"
        __key = __INVERT_KEY_INPUT_KEY
        invert_key_input = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Local copy"
        __key = __LOCAL_KEY
        local = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Minimum character speed"
        __key = __MIN_CHAR_SPEED_KEY
        min_char_speed = user_config.getint(__CONFIG_SECTION, __key)
        __option = "Remote send"
        __key = __REMOTE_KEY
        remote = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Text speed"
        __key = __TEXT_SPEED_KEY
        text_speed = user_config.getint(__CONFIG_SECTION, __key)
        __option = "Server URL"
        __key = __SERVER_URL_KEY
        _server_url = user_config.get(__CONFIG_SECTION, __key)
        if (not _server_url) or (_server_url.upper() != "NONE"):
            server_url = _server_url
        __option = "Sound"
        __key = __SOUND_KEY
        sound = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Sounder"
        __key = __SOUNDER_KEY
        sounder = user_config.getboolean(__CONFIG_SECTION, __key)
        __option = "Sounder power save (seconds)"
        __key = __SOUNDER_POWER_SAVE_KEY
        sounder_power_save = user_config.getint(__CONFIG_SECTION, __key)
        __option = "Spacing"
        __key = __SPACING_KEY
        _spacing = (user_config.get(__CONFIG_SECTION, __key)).upper()
        if _spacing == "NONE":
            spacing = Spacing.none
        elif _spacing == "CHAR":
            spacing = Spacing.char
        elif _spacing == "WORD":
            spacing = Spacing.word
        else:
            raise ValueError(_spacing)
        __option = "Station"
        __key = __STATION_KEY
        _station = user_config.get(__CONFIG_SECTION, __key)
        if (not _station) or (_station.upper() != "NONE"):
            station = _station
        __option = "Wire"
        __key = __WIRE_KEY
        _wire = user_config.get(__CONFIG_SECTION, __key)
        if (_wire) or (_wire.upper() != "NONE"):
            try:
                wire = int(_wire)
            except ValueError as ex:
                # log.err("Wire number value '{}' is not a valid integer value.".format(_wire))
                wire = 1
    except KeyError as ex:
        log.err("Key '{}' not found in configuration file.".format(ex.args[0]))
        raise
    except ValueError as ex:
        log.err("{} option value '{}' is not a valid value. INI file key: {}.".format(__option, ex.args[0], __key))
        raise

# ### Mainline
read_config()

auto_connect_override = argparse.ArgumentParser(add_help=False)
auto_connect_override.add_argument("-C", "--autoconnect", default="ON" if auto_connect else "OFF", 
choices=["ON", "On", "on", "YES", "Yes", "yes", "OFF", "Off", "off", "NO", "No", "no"], \
help="'ON' or 'OFF' to indicate whether an application should automatically connect to a configured wire.", \
metavar="auto-connect", dest="auto_connect")

code_type_override = argparse.ArgumentParser(add_help=False)
code_type_override.add_argument("-T", "--type", default=code_type.name.upper(), \
help="The code type (AMERICAN|INTERNATIONAL) to use.", metavar="code-type", dest="code_type")

interface_type_override = argparse.ArgumentParser(add_help=False)
interface_type_override.add_argument("-I", "--interface", default=interface_type.name.upper(), \
help="The interface type (KEY_SOUNDER|LOOP|KEYER) to use.", metavar="interface-type", dest="interface_type")

invert_key_input_override = argparse.ArgumentParser(add_help=False)
invert_key_input_override.add_argument("-M", "--iki", default=invert_key_input, \
help="Enable/disable inverting the key input signal (used for dial-up/modem connections).", metavar="invert-key-input", dest="invert_key_input")

local_override = argparse.ArgumentParser(add_help=False)
local_override.add_argument("-L", "--local", default=local, \
help="Enable/disable local copy of transmitted code.", metavar="local-copy", dest="local")

min_char_speed_override = argparse.ArgumentParser(add_help=False)
min_char_speed_override.add_argument("-c", "--charspeed", default=min_char_speed, type=int, \
help="The minimum character speed to use in words per minute (used for Farnsworth timing).", \
metavar="wpm", dest="min_char_speed")

remote_override = argparse.ArgumentParser(add_help=False)
remote_override.add_argument("-R", "--remote", default=remote, \
help="Enable/disable transmission over the internet on the specified wire.", \
metavar="remote-send", dest="remote")

server_url_override = argparse.ArgumentParser(add_help=False)
server_url_override.add_argument("-U", "--url", default=server_url, \
help="The KOB Server URL to use (or 'NONE' to use the default).", metavar="url", dest="server_url")

serial_port_override = argparse.ArgumentParser(add_help=False)
serial_port_override.add_argument("-p", "--port", default=serial_port, \
help="The name of the serial port to use (or 'NONE').", metavar="portname", dest="serial_port")

gpio_override = argparse.ArgumentParser(add_help=False)
gpio_override.add_argument("-g", "--gpio", default="ON" if gpio else "OFF",
choices=["ON", "On", "on", "YES", "Yes", "yes", "OFF", "Off", "off", "NO", "No", "no"], \
help="'ON' or 'OFF' to indicate whether GPIO (Raspberry Pi) key/sounder interface should be used.\
 GPIO takes priority over the serial interface.", \
metavar="gpio", dest="gpio")

sound_override = argparse.ArgumentParser(add_help=False)
sound_override.add_argument("-a", "--sound", default="ON" if sound else "OFF",
choices=["ON", "On", "on", "YES", "Yes", "yes", "OFF", "Off", "off", "NO", "No", "no"], \
help="'ON' or 'OFF' to indicate whether computer audio should be used to simulate a sounder.", \
metavar="sound", dest="sound")

sounder_override = argparse.ArgumentParser(add_help=False)
sounder_override.add_argument("-A", "--sounder", default="ON" if sounder else "OFF",
choices=["ON", "On", "on", "YES", "Yes", "yes", "OFF", "Off", "off", "NO", "No", "no"], \
help="'ON' or 'OFF' to indicate whether to use sounder if `port` is configured.", \
metavar="sounder", dest="sounder")

sounder_pwrsv_override = argparse.ArgumentParser(add_help=False)
sounder_pwrsv_override.add_argument("-P", "--pwrsv", default=sounder_power_save, type=int, \
help="The sounder power-save delay in seconds, or '0' to disable.", \
metavar="seconds", dest="sounder_power_save")

spacing_override = argparse.ArgumentParser(add_help=False)
spacing_override.add_argument("-s", "--spacing", default=spacing.name.upper(), \
help="The spacing (NONE|CHAR|WORD) to use.", metavar="spacing", dest="spacing")

station_override = argparse.ArgumentParser(add_help=False)
station_override.add_argument("-S", "--station", default=station, \
help="The Station ID to use (or 'NONE').", metavar="station", dest="station")

text_speed_override = argparse.ArgumentParser(add_help=False)
text_speed_override.add_argument("-t", "--textspeed", default=text_speed, type=int, \
help="The morse text speed in words per minute.", metavar="wpm", dest="text_speed")

wire_override = argparse.ArgumentParser(add_help=False)
wire_override.add_argument("-W", "--wire", default=wire, \
help="The Wire to use (or 'NONE').", metavar="wire", dest="wire")

