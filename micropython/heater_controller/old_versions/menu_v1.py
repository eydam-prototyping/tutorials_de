import machine
import ep_lcd_menu
from rotary_irq_esp import RotaryIRQ
from esp8266_i2c_lcd import I2cLcd

def setup():
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

    lcd = I2cLcd(i2c, 39, 2, 16)
    lcd.clear()

    r = RotaryIRQ(18, 19, 0, 10, False)

    menu = ep_lcd_menu.menu_rot_enc(
        menu_config_file="menu.json", display_type="1602", display=lcd, rotary=r, button_pin=5)

    menu.load()
    menu.render()
    return menu
