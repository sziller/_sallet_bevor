"""All Widgets and Layouts defined for the main Python file"""

from kivy.app import App  # necessary for the App class
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView

from SalletBasePackage.decorators import *
from SalletBasePackage.models import Utxo
from SalletNodePackage.BitcoinNodeObject import Node


# -----------------------------------------------------------------------------------------------
# - Labels                                                              Labels      -   START   -
# -----------------------------------------------------------------------------------------------
class LabelSallet(Label):
    """custom Label"""
    pass


class LabelInfo(LabelSallet):
    """custom Label"""
    pass


class LabelWelcomeTitle(LabelSallet):
    """custom Label"""
    pass


class LabelWelcomeIntro(LabelSallet):
    """custom Label"""
    pass


class LabelTitle(LabelSallet):
    """custom Label"""
    pass


class LabelSubTitle(LabelSallet):
    """custom Label"""
    pass


class LabelSubSubTitle(LabelSallet):
    """custom Label"""
    pass


class LabelListitem(LabelSallet):
    """custom Label"""
    pass


class LabelLead(LabelListitem):
    """custom Label"""
    pass


class LabelEnd(LabelListitem):
    """custom Label"""
    pass


class LabelWelcomeList(LabelSallet):
    """custom Label"""
    pass


class LabelWelcomeListLeft(LabelSallet):
    """custom Label"""
    pass


class ScreenTitleLabel(LabelSallet):
    """custom Label"""
    pass
# -----------------------------------------------------------------------------------------------
# - Labels                                                              Labels      -   ENDED   -
# -----------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------
# - Button                                                              Button      -   START   -
# -----------------------------------------------------------------------------------------------
class ButtonSallet(Button):
    """custom Button"""
    pass


class ButtonScreenNav(ButtonSallet):
    """custom Button"""
    pass


class ButtonBig(ButtonSallet):
    """custom Button"""
    pass
    

class ButtonListitem(ButtonSallet):
    """custom Button"""
    pass


class ButtonInfo(ButtonSallet):
    """custom Button"""
    pass


class ToggleButtonSallet(ToggleButton):
    """custom ToggleButton"""
    pass
# -----------------------------------------------------------------------------------------------
# - Button                                                              Button      -   ENDED   -
# -----------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------
# - TextInput                                                        TextInput      -   START   -
# -----------------------------------------------------------------------------------------------
class TextInputSallet(TextInput):
    """custom TextInput"""
    pass


class TextInputLineSallet(TextInputSallet):
    """custom TextInput"""
    pass


class TextInputParagraphSallet(TextInputSallet):
    """custom TextInput"""
    pass


class TextInputBrowser(TextInputParagraphSallet):
    """custom TextInput"""
    pass


class TextShowTx(TextInputParagraphSallet):
    """custom TextInput"""
    pass


class TextInpEntropySel(TextInputLineSallet):
    """custom TextInput"""
    pass
# -----------------------------------------------------------------------------------------------
# - TextInput                                                        TextInput      -   ENDED   -
# -----------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------
# - ScrollView                                                       ScrollView     -   START   -
# -----------------------------------------------------------------------------------------------
class ScrollViewSallet(ScrollView):
    """custom ScrollView"""
    pass
# -----------------------------------------------------------------------------------------------
# - ScrollView                                                       ScrollView     -   ENDED   -
# -----------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------
# - Layouts                                                         Layouts         -   START   -
# -----------------------------------------------------------------------------------------------
class Ribbon(BoxLayout):
    """custom Layout"""
    pass


class TitleLine(BoxLayout):
    """custom Layout"""
    pass


class UtxoDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(UtxoDisplayArea, self).__init__(**kwargs)


class InputDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(InputDisplayArea, self).__init__(**kwargs)


class OutputDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(OutputDisplayArea, self).__init__(**kwargs)


class NodeDisplayArea(StackLayout):
    def __init__(self, **kwargs):
        super(NodeDisplayArea, self).__init__(**kwargs)


class OperationAreaBox(BoxLayout):
    """custom BoxLayout"""
    pass


class OutputRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, n: int, parent_op_area: OperationAreaBox, **kwargs):
        super(OutputRowObj, self).__init__(**kwargs)
        self.parent_op_area: OperationAreaBox = parent_op_area
        self.n: int = n
        self.value: int = 0
        self.script_type: str = "p2pkh"
        self.script: str = ""

        self.lbl_n = LabelLead(text=str(self.n))
        self.lbl_n.size_hint = (0.1, 1)
        self.add_widget(self.lbl_n)

        self.lbl_pl1 = LabelLead(text="style")
        self.lbl_pl1.size_hint = (0.15, 1)
        self.add_widget(self.lbl_pl1)

        self.txtinp_addr = TextInputSallet()
        self.txtinp_addr.bind(text=self.read_addr)
        self.txtinp_addr.size_hint = (0.2, 1)
        self.add_widget(self.txtinp_addr)

        self.txtinp_value = TextInputSallet()
        self.txtinp_value.bind(text=self.read_value)
        self.txtinp_value.size_hint = (0.2, 1)
        self.add_widget(self.txtinp_value)

        if n:
            self.btn_del = ButtonListitem(text="-")
            self.btn_del.bind(on_release=self.del_this_row)
            self.btn_del.size_hint = (0.05, 1)
            self.add_widget(self.btn_del)
            self.btn_add = ButtonListitem(text="+")
            self.btn_add.size_hint = (0.05, 1)
        else:
            self.btn_add = ButtonListitem(text="+")
            self.btn_add.size_hint = (0.1, 1)
        self.btn_add.bind(on_release=self.add_next_row)
        self.add_widget(self.btn_add)
        
        self.tgl_nft = ToggleButtonSallet(text="nft")
        self.tgl_nft.size_hint = (0.05, 1)
        self.tgl_nft.bind(on_release=self.toggle_nft_use)
        self.add_widget(self.tgl_nft)
        
        self.lbl_scrollbar = LabelEnd()
        self.lbl_scrollbar.size_hint = (0.2, 1)
        self.add_widget(self.lbl_scrollbar)
        
    # Local methods to be called on generated Widget's action - redirecting to higher hierarchy object  -   START   -
    def add_next_row(self, inst=None, **kwargs):
        """=== Method name: add_next_row ===============================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Method to be triggered on adding a row.
        ========================================================================================== by Sziller ==="""
        self.btn_add.disabled = True
        self.parent_op_area.add_new_output_rowobj()

    def del_this_row(self, inst=None, **kwargs):
        """=== Method name: del_this_row ===============================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Method to be triggered on deleting a row.
        ========================================================================================== by Sziller ==="""
        self.parent_op_area.del_output(n=self.n)

    def update_n(self):
        """=== Method name: update_n ===================================================================================
        Method writes actual 'n' value into matching Label
        ========================================================================================== by Sziller ==="""
        self.lbl_n.text = str(self.n)

    def read_value(self, inst, value):
        """=== Method name: read_value =================================================================================
        Method to be called by generated Widget (Button or similar), and to activate subsequent actions in parent
        OperationArea.
        Handling data received by Widget.
        ========================================================================================== by Sziller ==="""
        print(type(value))
        try:
            self.value = float(value)
        except ValueError:
            print("Use numbers please!")
        self.parent_op_area.use_output_data()

    def read_addr(self, inst, value):
        """ TBD """
        print(value)

    # Local methods to be called on generated Widget's action - redirecting to higher hierarchy object  -   ENDED   -
    
    def toggle_nft_use(self, inst, **kwargs):
        print("yeeeee......")
        print(inst.state)
    

class NodeRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, node_obj: Node, parent_op_area: OperationAreaBox, **kwargs):
        super(NodeRowObj, self).__init__(**kwargs)
        self.node_obj = node_obj
        self.parent_op_area: OperationAreaBox = parent_op_area
        
        self.lbl_alias              = LabelWelcomeList(text=self.node_obj.alias)
        self.lbl_ip                 = LabelWelcomeListLeft(text=self.node_obj.ip)
        self.lbl_port               = LabelWelcomeListLeft(text=str(self.node_obj.port))
        self.lbl_owner              = LabelWelcomeListLeft(text=self.node_obj.owner)
        self.lbl_desc               = LabelLead(text=self.node_obj.desc)
        self.btn_use                = ButtonSallet(text="use")
        self.btn_use.bind(on_release=self.use_this_node)
        self.lbl_scrollbar          = LabelEnd(text=" - ")

        self.lbl_alias.size_hint        = (0.2, 1)
        self.lbl_ip.size_hint           = (0.175, 1)
        self.lbl_port.size_hint         = (0.1, 1)
        self.lbl_owner.size_hint        = (0.225, 1)
        self.lbl_desc.size_hint         = (0.25, 1)
        self.btn_use.size_hint          = (0.03, 1)
        self.lbl_scrollbar.size_hint    = (0.02, 1)
        
        self.add_widget(self.lbl_alias)
        self.add_widget(self.lbl_ip)
        self.add_widget(self.lbl_port)
        self.add_widget(self.lbl_owner)
        self.add_widget(self.lbl_desc)
        self.add_widget(self.btn_use)
        self.add_widget(self.lbl_scrollbar)

    def use_this_node(self, inst=None, **kwargs):
        """=== Method to use actual Node to broadcast Transaction(s)"""
        print("Button pushed: <use_this_node>")
        self.disabled = True
        self.parent_op_area.use_node(node=self.node_obj)
        
        
class UtxoRowObj(BoxLayout):
    orientation = "horizontal"

    def __init__(self, utxo_obj: Utxo, parent_op_area: OperationAreaBox, field: str = "utxo", **kwargs):
        super(UtxoRowObj, self).__init__(**kwargs)
        self.utxo_obj = utxo_obj
        self.uxto_id_obj = self.utxo_obj.utxo_id
        self.value: float = self.utxo_obj.value
        self.parent_op_area: OperationAreaBox = parent_op_area
        self.field: str = field  # 'utxo' or 'input'

        self.lbl_id = LabelLead(text=self.uxto_id_obj.__repr__())
        self.lbl_id.size_hint = (0.75, 1)
        self.add_widget(self.lbl_id)
        
        self.lbl_value = LabelEnd(text="{}".format(self.value))
        self.lbl_value.size_hint = (0.175, 1)
        self.add_widget(self.lbl_value)
        
        if self.field == 'utxo':
            self.btn_mark   = ButtonListitem(text="use")
            self.btn_mark.bind(on_release=self.use_this_utxo)
            self.btn_mark.size_hint = (0.05, 1)
            self.add_widget(self.btn_mark)
        elif self.field == 'input':
            self.btn_mark = ButtonListitem(text="del")
            self.btn_mark.bind(on_release=self.remove_this_utxo)
            self.btn_mark.size_hint = (0.05, 1)
            self.add_widget(self.btn_mark)
            
        self.lbl_scrollbar = LabelEnd()
        self.lbl_scrollbar.size_hint = (0.025, 1)
        self.add_widget(self.lbl_scrollbar)

    def use_this_utxo(self, inst=None, **kwargs):
        """=== Method to use actual utxo as Transaction input"""
        print("Button pushed: <use_this_utxo>")
        self.disabled = True
        self.parent_op_area.use_utxo_as_input(self.uxto_id_obj)
        
    def remove_this_utxo(self, inst=None, **kwargs):
        """=== Method to use actual utxo as Transaction input"""
        print("Button pushed: <remove_this_utxo>")
        self.parent_op_area.disregard_utxo_as_input(self.uxto_id_obj)

# -----------------------------------------------------------------------------------------------
# - Layouts                                                         Layouts         -   ENDED   -
# -----------------------------------------------------------------------------------------------


class NavBar(BoxLayout):
    """=== Class name: NavBar ==========================================================================================
    This Layout can be used across all screens. Class handles complications of now yet drawn instances.
    It sets appearance for instances only appearing on screen.
    ============================================================================================== by Sziller ==="""

    @ staticmethod
    @ log_button_click
    def on_release_navbar(inst):
        """=== StaticMethod ============================================================================================
        Method manages multiple screen selection by Toggle button set.
        All Toggle Buttons call this same function. Their Class names are stored in the <buttons> list.
        Only one button of the entire set is down at a given time. Function is extendable.
        Once a given button is 'down', it becomes inactive, all other buttons are activated and set to "normal" state.
        The reason of the logic is as follows:
        Screen manager is the unit taking care of actual screen swaps, also it stores actually shown screen name.
        However, at the itme of instantiation of the Screen Manager's ids are still not accessible.
        So we refer to ScreenManager's id's only on user action.
        :var inst: - the instance (button) activating the Method.
        ========================================================================================== by Sziller ==="""
        # Retrieve the sequence number of the currently shown screen
        old_seq: int = 0
        for k, v in App.get_running_app().root.statedict.items():
            if k == App.get_running_app().root.current_screen.name:
                old_seq = v["seq"]
                break
        # Identify the sequence number of the target screen
        new_seq = App.get_running_app().root.statedict[inst.target]["seq"]

        # Change the screen based on the direction of the sequence change
        App.get_running_app().change_screen(screen_name=inst.target,
                                            screen_direction={True: "left", False: "right"}[old_seq - new_seq < 0])
        # Update button appearances based on the target screen's states
        for buttinst in App.get_running_app().root.current_screen.ids.navbar.ids:
            # Deactivate buttons linked to the target screen
            if buttinst in App.get_running_app().root.statedict[inst.target]['down']:
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].disabled = True
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].state = "normal"
            # Activate buttons not linked to the target screen
            if buttinst in App.get_running_app().root.statedict[inst.target]['normal']:
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].disabled = False
                App.get_running_app().root.current_screen.ids.navbar.ids[buttinst].state = "normal"
