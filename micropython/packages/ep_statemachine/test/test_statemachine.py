import unittest
import ep_statemachine as es
import re

class Test(unittest.TestCase):
    def test_init_1(self):
        s1 = es.state("start")
        s2 = es.state("end")

        t1 = es.transition(s2, "next", condition=lambda: True)
        s1.add_transition(t1)

        sm = es.statemachine([s1, s2])

        self.assertRaises(RuntimeError, sm.init)    # test if no initial state is definied

        s1.initial = True
        sm.init()
        sm.step()

        self.assertEqual(sm.state, s2)              # test if first transition works
        self.assertRaises(RuntimeError, sm.step)    # test if final state works right

    def test_coffee_machine(self):
        i = 0
        
        def inc():
            nonlocal i
            i = i + 1

        workflow = [
            "press coffee button",
            "press coffee button",
            "press espresso button",
            "press espresso button",
            "press off button",
            "press off button",
        ]

        
        s_sleep = es.state("sleep", initial=True, entry_action=inc)
        s_select_input = es.state("select_input", entry_action=inc)
        s_make_coffee = es.state("make coffee")
        s_make_espresso = es.state("make espresso")
        s_done = es.state("done")
        s_off = es.state("off")

        t_wake_up = es.transition(s_select_input, identifier="wake up", condition=lambda: re.match("press (coffee|espresso|off) button", workflow[i]) is not None)
        s_sleep.add_transition(t_wake_up)
        
        t_coffee = es.transition(s_make_coffee, identifier="coffee", condition=lambda: workflow[i] == "press coffee button")
        s_select_input.add_transition(t_coffee)
        
        t_espresso = es.transition(s_make_espresso, identifier="espresso", condition=lambda: workflow[i] == "press espresso button")
        s_select_input.add_transition(t_espresso)
        
        t_finished = es.transition(s_done, identifier="finished", condition=lambda: True)
        s_make_coffee.add_transition(t_finished)
        s_make_espresso.add_transition(t_finished)

        t_back_to_sleep = es.transition(s_sleep, identifier="back to sleep", condition=lambda: True)
        s_done.add_transition(t_back_to_sleep)

        t_turn_off = es.transition(s_off, identifier="turn off", condition=lambda:workflow[i] == "press off button")
        s_select_input.add_transition(t_turn_off)

        sm = es.statemachine([s_sleep, s_select_input, s_make_coffee, s_make_espresso, s_done, s_off])

        sm.init()
        self.assertEqual(sm.state, s_sleep)
        sm.step() # press any button
        self.assertEqual(sm.state, s_select_input)
        sm.step() # press coffee button
        self.assertEqual(sm.state, s_make_coffee)
        sm.step() # wait
        self.assertEqual(sm.state, s_done)
        sm.step() # drink coffee
        self.assertEqual(sm.state, s_sleep)
        sm.step() # press any button
        self.assertEqual(sm.state, s_select_input)
        sm.step() # press espresso button
        self.assertEqual(sm.state, s_make_espresso)
        sm.step() # wait
        self.assertEqual(sm.state, s_done)
        sm.step() # drink espresso
        self.assertEqual(sm.state, s_sleep)
        sm.step() # press off button
        self.assertEqual(sm.state, s_select_input)
        sm.step() # press off button
        self.assertEqual(sm.state, s_off)
        self.assertRaises(RuntimeError, sm.step)    # coffee machine is off

        sm.init() # reinit
        i = 0
        self.assertEqual(sm.state, s_sleep)
        sm.cycle(0.01) # run all steps at once
        self.assertEqual(sm.state, s_off)

    def test_coffee_machine_event(self):
        s_sleep = es.state("sleep", initial=True)
        s_select_input = es.state("select_input")
        s_make_coffee = es.state("make coffee")
        s_make_espresso = es.state("make espresso")
        s_done = es.state("done")
        s_off = es.state("off")

        e_press_coffee_button = es.event("coffee button pressed")
        e_press_espresso_button = es.event("espresso button pressed")
        e_press_off_button = es.event("off button pressed")


        t_wake_up = es.transition(s_select_input, identifier="wake up", events=[e_press_coffee_button, e_press_espresso_button, e_press_off_button])
        s_sleep.add_transition(t_wake_up)
        
        t_coffee = es.transition(s_make_coffee, identifier="coffee", events=[e_press_coffee_button])
        s_select_input.add_transition(t_coffee)
        
        t_espresso = es.transition(s_make_espresso, identifier="espresso", events=[e_press_espresso_button])
        s_select_input.add_transition(t_espresso)

        t_finished = es.transition(s_done, identifier="finished", condition=lambda: True)
        s_make_coffee.add_transition(t_finished)
        s_make_espresso.add_transition(t_finished)

        t_back_to_sleep = es.transition(s_sleep, identifier="back to sleep", condition=lambda: True)
        s_done.add_transition(t_back_to_sleep)
        
        t_turn_off = es.transition(s_off, identifier="turn off", events=[e_press_off_button])
        s_select_input.add_transition(t_turn_off)
        

        sm = es.statemachine([s_sleep, s_select_input, s_make_coffee, s_make_espresso, s_done, s_off])
        sm.init()
        self.assertEqual(sm.state, s_sleep)
        sm.action(e_press_coffee_button)
        self.assertEqual(sm.state, s_select_input)
        sm.action(e_press_coffee_button)
        self.assertEqual(sm.state, s_make_coffee)
        sm.step()
        self.assertEqual(sm.state, s_done)
        sm.step()
        self.assertEqual(sm.state, s_sleep)
        sm.action(e_press_coffee_button)
        self.assertEqual(sm.state, s_select_input)
        sm.action(e_press_espresso_button)
        self.assertEqual(sm.state, s_make_espresso)
        sm.step()
        self.assertEqual(sm.state, s_done)
        sm.step()
        self.assertEqual(sm.state, s_sleep)
        sm.action(e_press_off_button)
        self.assertEqual(sm.state, s_select_input)
        sm.action(e_press_off_button)
        self.assertEqual(sm.state, s_off)


    def test_heater_control(self):
        i = 0

        def inc():
            nonlocal i
            i = i + 1

        s_cold = es.state("cold", initial=True, entry_action=inc, during_action=inc) # 1
        s_heat_up_1 = es.state("head up 1", entry_action=inc, during_action=inc)     # 2
        s_heat_up_2 = es.state("head up 2", entry_action=inc, during_action=inc)     # 3
        s_hot = es.state("hot", entry_action=inc, during_action=inc)                 # 4
        s_to_hot = es.state("to hot", entry_action=inc, during_action=inc)           # 5
        s_much_to_hot = es.state("much to hot", entry_action=inc, during_action=inc) # 6
        s_cool_down = es.state("much to hot", entry_action=inc, during_action=inc)   # 7
        

        # test array:
        # state is state before temperatures are reached
        test_array = [
            {"T_Oven": 40, "T_Tank_Upper": 30, "T_Tank_Lower": 25, "state": s_cold},
            {"T_Oven": 50, "T_Tank_Upper": 30, "T_Tank_Lower": 25, "state": s_cold},
            {"T_Oven": 60, "T_Tank_Upper": 30, "T_Tank_Lower": 25, "state": s_cold},
            {"T_Oven": 70, "T_Tank_Upper": 30, "T_Tank_Lower": 25, "state": s_cold},
            {"T_Oven": 70, "T_Tank_Upper": 40, "T_Tank_Lower": 25, "state": s_heat_up_1},
            {"T_Oven": 70, "T_Tank_Upper": 50, "T_Tank_Lower": 30, "state": s_heat_up_1},
            {"T_Oven": 70, "T_Tank_Upper": 50, "T_Tank_Lower": 40, "state": s_heat_up_1},
            {"T_Oven": 60, "T_Tank_Upper": 60, "T_Tank_Lower": 50, "state": s_heat_up_1},
            {"T_Oven": 55, "T_Tank_Upper": 60, "T_Tank_Lower": 50, "state": s_heat_up_1},
            {"T_Oven": 55, "T_Tank_Upper": 60, "T_Tank_Lower": 55, "state": s_heat_up_2},
            {"T_Oven": 60, "T_Tank_Upper": 60, "T_Tank_Lower": 55, "state": s_heat_up_2},
            {"T_Oven": 70, "T_Tank_Upper": 60, "T_Tank_Lower": 55, "state": s_heat_up_2},
            {"T_Oven": 75, "T_Tank_Upper": 60, "T_Tank_Lower": 55, "state": s_heat_up_1},
            {"T_Oven": 85, "T_Tank_Upper": 80, "T_Tank_Lower": 70, "state": s_heat_up_1},
            {"T_Oven": 85, "T_Tank_Upper": 80, "T_Tank_Lower": 70, "state": s_hot},
            {"T_Oven": 90, "T_Tank_Upper": 80, "T_Tank_Lower": 70, "state": s_hot},
            {"T_Oven": 97, "T_Tank_Upper": 80, "T_Tank_Lower": 70, "state": s_hot},
            {"T_Oven": 97, "T_Tank_Upper": 80, "T_Tank_Lower": 70, "state": s_to_hot},
            {"T_Oven": 90, "T_Tank_Upper": 80, "T_Tank_Lower": 75, "state": s_to_hot},
            {"T_Oven": 90, "T_Tank_Upper": 80, "T_Tank_Lower": 75, "state": s_hot},
            {"T_Oven": 97, "T_Tank_Upper": 80, "T_Tank_Lower": 75, "state": s_hot},
            {"T_Oven": 97, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_to_hot},
            {"T_Oven": 101, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_to_hot},
            {"T_Oven": 101, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_much_to_hot},
            {"T_Oven": 101, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_much_to_hot},
            {"T_Oven": 97, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_much_to_hot},
            {"T_Oven": 97, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_to_hot},
            {"T_Oven": 90, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_to_hot},
            {"T_Oven": 90, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_hot},
            {"T_Oven": 80, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_hot},
            {"T_Oven": 70, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_hot},
            {"T_Oven": 60, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_hot},
            {"T_Oven": 55, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_hot},
            {"T_Oven": 55, "T_Tank_Upper": 85, "T_Tank_Lower": 80, "state": s_cool_down},
        ]

        t_12 = es.transition(s_heat_up_1, identifier="t_12", condition=lambda: (test_array[i]["T_Oven"] > 65) & (test_array[i]["T_Oven"] > test_array[i]["T_Tank_Lower"] ))
        s_cold.add_transition(t_12)
        
        t_23 = es.transition(s_heat_up_2, identifier="t_23", condition=lambda: (test_array[i]["T_Oven"] < 60) | (test_array[i]["T_Tank_Lower"] > test_array[i]["T_Oven"]))
        s_heat_up_1.add_transition(t_23)
        
        t_32 = es.transition(s_heat_up_1, identifier="t_32", condition=lambda: (test_array[i]["T_Oven"] > test_array[i]["T_Tank_Lower"] + 5))
        s_heat_up_2.add_transition(t_32)

        t_24 = t_34 = es.transition(s_hot, identifier="t_x4", condition=lambda: (test_array[i]["T_Oven"] > 80))
        s_heat_up_1.add_transition(t_24)
        s_heat_up_2.add_transition(t_34)

        t_45 = es.transition(s_to_hot, identifier="t_45", condition=lambda: (test_array[i]["T_Oven"] > 96))
        t_54 = es.transition(s_hot, identifier="t_54", condition=lambda: (test_array[i]["T_Oven"] < 94))
        s_hot.add_transition(t_45)
        s_to_hot.add_transition(t_54)

        t_56 = es.transition(s_much_to_hot, identifier="t_56", condition=lambda: (test_array[i]["T_Oven"] > 100))
        t_65 = es.transition(s_to_hot, identifier="t_65", condition=lambda: (test_array[i]["T_Oven"] < 98))
        s_to_hot.add_transition(t_56)
        s_much_to_hot.add_transition(t_65)

        t_47 = es.transition(s_cool_down, identifier="t_47", condition=lambda: (test_array[i]["T_Oven"] < 60))
        s_hot.add_transition(t_47)

        t_71 = es.transition(s_cold, identifier="t_71", condition=lambda: (test_array[i]["T_Oven"] < 50))
        s_cool_down.add_transition(t_71)

        t_72 = es.transition(s_heat_up_1, identifier="t_72", condition=lambda: (test_array[i]["T_Oven"] > 60) & (test_array[i]["T_Oven"] > test_array[i]["T_Tank_Lower"]))
        s_cool_down.add_transition(t_72)

        t_37 = es.transition(s_cool_down, identifier="t_37", condition=lambda: (test_array[i]["T_Oven"] < 60))
        s_cool_down.add_transition(t_37)

        sm = es.statemachine([s_cold, s_heat_up_1, s_heat_up_2, s_hot, s_to_hot, s_much_to_hot, s_cool_down])
        sm.init()

        while i < len(test_array):
            self.assertEqual(sm.state, test_array[i]["state"])
            sm.step()
        
