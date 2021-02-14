import machine
import ep_lcd_menu
from rotary_irq_esp import RotaryIRQ
from esp8266_i2c_lcd import I2cLcd
import esp32
import gc


def setup(temps, sm):
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

    lcd = I2cLcd(i2c, 39, 2, 16)
    lcd.clear()

    r = RotaryIRQ(18, 19, 0, 10, False)

    menu = ep_lcd_menu.menu_rot_enc(
        menu_config_file="menu.json", display_type="1602", display=lcd, rotary=r, button_pin=5)

    menu.display_funcs = {
        "print_T_Oven": lambda: "{:.2f} C".format(temps("T_Oven")),
        "print_T_TankU": lambda: "{:.2f} C".format(temps("T_TankU")),
        "print_T_TankL": lambda: "{:.2f} C".format(temps("T_TankL")),
        "print_state": lambda: "{}".format(sm.state),
        "print_cpu_temp": lambda: "{:.2f} C".format((esp32.raw_temperature()-32)*5/9),
        "print_ram": lambda: "{:.1f}/{:.1f}kB".format(gc.mem_free()/1024, (gc.mem_alloc()+gc.mem_free())/1024),
    }

    menu.load()
    menu.render()
    return menu
