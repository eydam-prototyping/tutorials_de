import ep_statemachine
import machine

def setup(temps, thresh):
    pump_pin = machine.Pin(14, machine.Pin.OUT)
    warn_led = machine.Pin(17, machine.Pin.OUT)

    pump_on = lambda: pump_pin.off()
    pump_off = lambda: pump_pin.on()

    warn_on = lambda: warn_led.off()
    warn_off = lambda: warn_led.on()

    def s_cold_enter():
        pump_off()
        warn_off()

    def s_heatUp1_enter():
        pump_on()
        warn_off()

    def s_heatUp2_enter():
        pump_off()
        warn_off()

    def s_hot_enter():
        pump_off()
        warn_off()

    def s_toHot_enter():
        pump_on()
        warn_on()

    def s_muchToHot_enter():
        pump_on()
        warn_on()

    s_cold = ep_statemachine.state("cold", initial=True, entry_action=s_cold_enter)    #1
    s_heatUp1 = ep_statemachine.state("heatUp1", entry_action=s_heatUp1_enter)         #2
    s_heatUp2 = ep_statemachine.state("heatUp2", entry_action=s_heatUp2_enter)         #3
    s_hot = ep_statemachine.state("hot", entry_action=s_hot_enter)                     #4
    s_toHot = ep_statemachine.state("toHot", entry_action=s_toHot_enter)               #5
    s_muchToHot = ep_statemachine.state("muchToHot", entry_action=s_muchToHot_enter)   #6

    t_12 = ep_statemachine.transition(s_heatUp1, "t_12",                # (T_Oven > T1) & T_Oven > T_TankU + dT1
        lambda: (temps("T_Oven")>thresh("T1")) & (temps("T_Oven")>temps("T_TankU")+thresh("T1")) 
        )

    t_23 = ep_statemachine.transition(s_heatUp2, "t_23", 
        lambda: (temps("T_Oven")<temps("T_TankL")+thresh("dT1"))        # T_Oven < T_TankL + dT1
        )

    t_32 = ep_statemachine.transition(s_heatUp1, "t_32", 
        lambda: (temps("T_Oven")>temps("T_TankU")+thresh("dT1"))        # T_Oven > T_TankU + dT1
        )

    t_cold = ep_statemachine.transition(s_cold, "t_cold", 
        lambda: (temps("T_Oven")<thresh("T5"))                          # T_Oven < T5
        )

    t_hot = ep_statemachine.transition(s_hot, "t_hot", 
        lambda: (temps("T_TankL")>thresh("T2"))                         # T_TankL > T2
        )

    t_42 = ep_statemachine.transition(s_heatUp1, "t_42",                # T_TankL < T2 - dT1 & T_Oven > T_TankU + dT1
        lambda: (temps("T_TankL")<thresh("T2")-thresh("dT1"))&(temps("T_Oven")>temps("T_TankU")+thresh("dT1"))        
        )

    t_toHot = ep_statemachine.transition(s_toHot, "t_toHot",          
        lambda: (temps("T_Oven")>thresh("T3")+thresh("dT2"))            # T_Oven > T3 + dT2
        )

    t_54 = ep_statemachine.transition(s_hot, "t_54",          
        lambda: (temps("T_Oven")<thresh("T3")-thresh("dT2"))            # T_Oven < T3 - dT2
        )

    t_56 = ep_statemachine.transition(s_muchToHot, "t_56",          
        lambda: (temps("T_Oven")>thresh("T4")+thresh("dT2"))            # T_Oven > T4 + dT2
        )

    t_65 = ep_statemachine.transition(s_toHot, "t_65",          
        lambda: (temps("T_Oven")<thresh("T4")-thresh("dT2"))            # T_Oven < T4 - dT2
        )

    s_cold.add_transition(t_12)
    s_cold.add_transition(t_toHot)

    s_heatUp1.add_transition(t_23)
    s_heatUp1.add_transition(t_cold)
    s_heatUp1.add_transition(t_hot)
    s_heatUp1.add_transition(t_toHot)

    s_heatUp2.add_transition(t_32)
    s_heatUp2.add_transition(t_cold)
    s_heatUp2.add_transition(t_hot)
    s_heatUp2.add_transition(t_toHot)
    
    s_hot.add_transition(t_cold)
    s_hot.add_transition(t_toHot)
    s_hot.add_transition(t_42)

    s_toHot.add_transition(t_54)
    s_toHot.add_transition(t_56)

    s_muchToHot.add_transition(t_65)

    return ep_statemachine.statemachine([s_cold, s_heatUp1, s_heatUp2, s_hot, s_toHot, s_muchToHot])