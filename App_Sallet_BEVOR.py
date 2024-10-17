"""Sallet univers' BEVOR app.
by Sziller"""

import os
import sys
import cv2
import dotenv
import inspect
from kivy.app import App  # necessary for the App class
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.graphics.texture import Texture

from SalletBasePackage.WidgetClasses import *
from SalletBasePackage import SQL_interface as sql, models
from SalletBasePackage import units
from SalletBasePackage import DataDisplay as DaDi
from SalletNodePackage import NodeManager as NodeMan
from SalletNodePackage import BitcoinNodeObject as BtcNode


from kivy.config import Config

DOTENV_PATH = "./.env"

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

WELCOME_TITLE       = "Welcome to Sallet - protecting your assets!"
WELCOME_TXT         = ("This is the Bevor module of the Sallet Universe: "
                       "This is a Node manager application. \n"
                       "The Sallet system was built with security in focus. "
                       "When planing security we at sziller.eu hope for the"
                       "best and plan for the worst.")
FEATURE_SET         = ("- Manage and select your own Node")
FEATURE_ALIASES     = ("- Coin selection\n"
                       "- No digital footprint\n"
                       "- Hidden entropy\n"
                       "- Privacy\n"
                       "- Asset management\n"
                       "- Node selection")


class SalletScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(SalletScreenManager, self).__init__(**kwargs)
        self.statedict = {
            "screen_intro": {
                "seq": 0,
                'inst': "button_nav_intro",
                'down': ["button_nav_intro"],
                'normal': ["button_nav_btc", "button_nav_browse", "button_nav_command"]},
            "screen_btc": {
                "seq": 1,
                'inst': 'button_nav_btc',
                'down': ['button_nav_btc'],
                'normal': ["button_nav_intro", "button_nav_browse", "button_nav_command"]},
            "screen_browse": {
                "seq": 2,
                'inst': "button_nav_browse",
                'down': ["button_nav_browse"],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_command"]},
            "screen_command": {
                "seq": 3,
                'inst': "button_nav_command",
                'down': ["button_nav_command"],
                'normal': ["button_nav_intro", "button_nav_btc", "button_nav_browse"]}
            }


class NavBar(BoxLayout):
    """=== Class name: NavBar ==========================================================================================
    This Layout can be used across all screens. Class handles complications of now yet drawn instances.
    It sets appearance for instances only appearing on screen.
    ============================================================================================== by Sziller ==="""

    @ staticmethod
    def on_release_navbar(inst):
        """=== Method name: on_toggle_navbar ===========================================================================
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


class OpAreaIntro(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaIntro, self).__init__(**kwargs)

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))


class QRdisplay(BoxLayout):
    ccn = inspect.currentframe().f_code.co_name
    qr_list = os.listdir("./qrcodes")
    qr_counter = 0
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))

    def on_buttonclick_qr_browse(self, inst):
        """=== Method name: on_buttonclick_qr_browse ===================================================================
        ========================================================================================== by Sziller ==="""
        print("Pushed from QRdisplay")
        self.qr_counter += inst.add
        if self.qr_counter >= len(self.qr_list): self.qr_counter = 0
        if self.qr_counter < 0: self.qr_counter = len(self.qr_list) - 1
        self.ids.qr_count.text = str(self.qr_counter)
        self.ids.qr_plot_layout.remove_widget(self.ids.qr_plot_layout.displayed_qr)
        passed = AsyncImage(source="./qrcodes/" + self.qr_list[self.qr_counter])
        self.ids.qr_plot_layout.swap_displayed_qr_widget(received=passed)
        
        
class QRPlotField(BoxLayout):
    def __init__(self, **kwargs):
        super(QRPlotField, self).__init__(**kwargs)
        self.displayed_qr = Label(text="Images will be displayed here")
        self.add_widget(self.displayed_qr)

    def swap_displayed_qr_widget(self, received):
        """=== Method name: swap_displayed_qr_widget ===================================================================
        ========================================================================================== by Sziller ==="""
        print("Pushed from QRPlotLayout")
        self.remove_widget(self.displayed_qr)
        self.displayed_qr = received
        self.add_widget(self.displayed_qr)


class ScanArea(BoxLayout):
    def __init__(self, **kwargs):
        super(ScanArea, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 1920)
        self.cam.set(4, 1080)

        self.fps = 60
        self.schedule = None
        self.collected_strings = []

    def start_scanning(self):
        """=== Method name: start_scanning =============================================================================
        ========================================================================================== by Sziller ==="""
        self.schedule = Clock.schedule_interval(self.update, 1.0 / self.fps)

    def stop_scanning(self):
        """=== Method name: stop_scanning ==============================================================================
        ========================================================================================== by Sziller ==="""
        self.schedule.cancel()
        for _ in self.collected_strings:
            print(_)

    def update(self, dt):
        """=== Method name: update =====================================================================================
        ========================================================================================== by Sziller ==="""
        if True:
            ret, frame = self.cam.read()
            if ret:
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tobytes()
                image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

                self.ids.img.texture = image_texture

                barcodes = pyzbar.decode(frame)

                if not barcodes:
                    scan_img = cv2.putText(frame, 'Scanning', (50, 75), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 255), 2)
                    scan_buf = cv2.flip(scan_img, 0)
                    scan_buf = scan_buf.tobytes()
                    scan_texture = Texture.create(size=(scan_img.shape[1], scan_img.shape[0]), colorfmt='bgr')
                    scan_texture.blit_buffer(scan_buf, colorfmt='bgr', bufferfmt='ubyte')

                    self.ids.img.texture = scan_texture

                else:
                    for barcode in barcodes:
                        (x, y, w, h) = barcode.rect
                        rectangle_img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 7)
                        rectangle_buf = cv2.flip(rectangle_img, 0)
                        rectangle_buf = rectangle_buf.tobytes()
                        rectangle_texture = Texture.create(size=(rectangle_img.shape[1], rectangle_img.shape[0]),
                                                           colorfmt='bgr')
                        rectangle_texture.blit_buffer(rectangle_buf, colorfmt='bgr', bufferfmt='ubyte')

                        self.ids.img.texture = rectangle_texture

                        actual_text = str(barcode.data.decode("utf-8"))
                        print(actual_text)
                        if actual_text not in self.collected_strings:
                            self.collected_strings.append(actual_text)


class OpAreaQrIn(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaQrIn, self).__init__(**kwargs)
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
    def on_toggle_scan_qr(self, inst):
        """=== Method name: on_toggle_scan_qr ==========================================================================
        ========================================================================================== by Sziller ==="""
        
        if inst.state == "normal":
            self.ids.scan_area.stop_scanning()
            inst.text = "scanning stopped"
            self.ids.scan_area.ids.img.texture = None
            self.ids.scan_area.ids.img.reload()
        else:
            self.ids.scan_area.start_scanning()
            inst.text = "now scanning..."
        print("toggled camera on/off")


class OpAreaBtc (OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaBtc, self).__init__(**kwargs)
    
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))
        
        
class OpAreaNft (OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaNft, self).__init__(**kwargs)
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))


class OpAreaMint(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self, **kwargs):
        super(OpAreaMint, self).__init__(**kwargs)

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))


class OpAreaBrowse(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self, **kwargs):
        super(OpAreaBrowse, self).__init__(**kwargs)
        self.memorized_btn_color: tuple or None = None  # workaround to gain button color from .kv
        self.memorized_btn_text: str or None = None  # workaround to gain button text from .kv

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        pass
        
    def on_textupdate_textinput(self, inst):
        pass
        # print(inst.text)
    
    def on_buttonclick_browse(self, inst):
        if self.memorized_btn_color is None:
            self.memorized_btn_color = inst.background_color
            self.memorized_btn_text = inst.text
        
        tx_id = self.ids.txtinp_browse.text
        print(tx_id)
        returned_json = {}
        
        try:
            returned_json = App.get_running_app().actual_node_object.nodeop_getrawtransaction(tx_hash=tx_id, verbose=1)
            inst.background_color = self.memorized_btn_color
            inst.text = self.memorized_btn_text
        except:
            inst.background_color = (1, 0, 0)
            inst.text = "INVALID"
        data_as_displayed = DaDi.rec_data_plotter(data=returned_json, string="")
        self.ids.lbl_tx_info.text = data_as_displayed
        
        
class OpAreaSend(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaSend, self).__init__(**kwargs)
        self.nodemanager: NodeMan.NODEManager or None   = None
        self.node_rowobj_dict_in_opareasend: dict = {}
        self.used_node: BtcNode.Node or None = None
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        self.nodemanager = NodeMan.NODEManager(session_in=App.get_running_app().db_session, dotenv_path="./.env")
        self.display_node_rowobj_list()
    
    def on_btn_release_broadcast(self):
        """=== Method name: on_btn_release_broadcast ===================================================================
        actions taken when button pushed.
        ========================================================================================== by Sziller ==="""
        print("PUSHED: on_btn_release_broadcast - says: {}".format(self.ccn))
    
    def on_btn_release_cancel(self):
        """=== Method name: on_btn_release_cancel ======================================================================
        actions taken when button pushed.
        ========================================================================================== by Sziller ==="""
        print("PUSHED: on_btn_release_cancel - says: {}".format(self.ccn))
    
    # def display_node_data(self):
    #     """=== Method name: display_node_data ========================================================================
    #     Method updates Utxo balance Label in current Object instance of OpAreaTx(OperationAreaBox)
    #     ========================================================================================== by Sziller ==="""
    #     self.ids.lbl_node_data.text = str(self.nodemanager.node_list)
    
    def display_node_rowobj_list(self):
        """=== Method name: add_new_node_rowobj ========================================================================
        Method checks number of outputs, and adds a new OutputRowObj to the output_display_area.
        It also updates any fields update logically affects.
        ========================================================================================== by Sziller ==="""
        for alias, node_rowobj in self.nodemanager.node_obj_dict.items():
            print(node_rowobj)
            newline = NodeRowObj(parent_op_area=self, node_obj=node_rowobj)
            self.ids.node_display_area.add_widget(newline)  # only add if key does not exist!!!
            self.node_rowobj_dict_in_opareasend[alias] = newline
        
    def use_node(self, node: BtcNode.Node):
        """=== Method name: use_node ===================================================================================
        ========================================================================================== by Sziller ==="""
        print(node)
        used_alias = node.alias
        for alias, node_rowobj in self.node_rowobj_dict_in_opareasend.items():
            if alias is not used_alias:
                node_rowobj.disabled = False
        self.ids.used_node_data.node_alias = node.alias
        self.ids.used_node_data.node_address = node.ip + ":" + str(node.port)


class OpAreaCommand(OperationAreaBox):
    """
    This class represents the operation area for the Command screen.
    It contains manually defined CommandRowObj instances and manages their activation and command execution.
    """

    def __init__(self, **kwargs):
        super(OpAreaCommand, self).__init__(**kwargs)
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        pass

    def activate_row(self, active_row):
        """
        Activates the specified row and deactivates all other rows.
        """
        for row in self.command_rows:
            row.set_active(row == active_row)

    def execute_command(self, row_number, parameters):
        """
        Executes the command for the given row with the provided parameters.
        """
        print(f"Executing command from row {row_number} with parameters: {parameters}")
        # Add your logic for executing the command here



class SalletBEVOR(App):
    """=== Class name: SalletBEVOR =====================================================================================
    Child of built-in class: App
    This is the Parent application for the Sealed of Kex manager project.
    Instantiation should - contrary to what is used on the net - happen by assigning it to a variable name.
    :param window_content:
    ============================================================================================== by Sziller ==="""
    def __init__(self, window_content: str, csm: float = 1.0, dotenv_path="./.env"):
        super(SalletBEVOR, self).__init__()
        self.window_content = window_content
        self.content_size_multiplier = csm
        self.dotenv_path: str = dotenv_path
        dotenv.load_dotenv(self.dotenv_path)
        self.title: str = "Sallet - Bevor: Command your Node"
        self.balance_onchain_sats: int = 0
        # --- Database settings ---------------------------------------------   - Database settings -   START   -
        self.db_session = sql.createSession(db_path=os.getenv("DB_PATH_BEVOR"),
                                            style=os.getenv("DB_STYLE_BEVOR"))
        # --- Database settings ---------------------------------------------   - Database settings -   ENDED   -

        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   START   -
        self.unit_base: str         = os.getenv("UNIT_BASE")
        self.unit_use: str          = os.getenv("UNIT_USE")
        self.display_format: str    = os.getenv("DISPLAY_FORMAT") + " " + os.getenv("UNIT_USE")
        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   ENDED   -
        # --- Node related settings -------------------------------------  Node related settings    -   START   -
        self.actual_node_object: BtcNode.Node or None = None
        # --- Node related settings -------------------------------------  Node related settings    -   START   -

    def change_screen(self, screen_name, screen_direction="left"):
        """=== Method name: change_screen ==============================================================================
        Use this screenchanger instead of the built-in method for more customizability and to enable further
        actions before changing the screen.
        Also, if screenchanging first needs to be validated, use this method!
        ========================================================================================== by Sziller ==="""
        smng = self.root  # 'root' refers to the only one root instance in your App. Here it is the actual ROOT
        smng.current = screen_name
        smng.transition.direction = screen_direction

    def build(self):
        """=== Method name: ============================================================================
        ========================================================================================== by Sziller ==="""
        return self.window_content
    
    def on_start(self):
        """=== Method name: on_start ===================================================================================
        Redefinition of a built-in function to be run after app is fully loaded with all it's subclasses instantiated
        ===========================================================================================by Sziller ==="""
        # --- Initiating each OpArea's <on_init> methods                                        START   -
        for screen_name, screen_obj in self.root.ids.items():
            for widget_name, widget_obj in screen_obj.ids.items():
                if widget_name.startswith("oparea_"):
                    widget_obj.on_init()
        # --- Initiating each OpArea's <on_init> methods                                        ENDED   -

        # --- Navigation-button handling                                                        START   -
        for navname, navbutton in self.root.ids.screen_intro.ids.navbar.ids.items():
            if navname == "button_nav_intro":
                navbutton.disabled = True
            else:
                navbutton.disabled = False
        # --- Navigation-button handling                                                        ENDED   -
        
        # --- Filling in large text-fields of Labels                                            START   -
        self.root.ids.screen_intro.ids.oparea_intro.ids.lbl_welcome_title.text = WELCOME_TITLE
        self.root.ids.screen_intro.ids.oparea_intro.ids.lbl_welcome_intro.text = WELCOME_TXT
        # --- Filling in large text-fields of Labels                                            ENDED   -
        # --- Setting default Node                                                              START   -
        self.actual_node_object = BtcNode.Node(is_rpc=True, dotenv_path=self.dotenv_path)
        # --- Setting default Node                                                              ENDED   -

        
if __name__ == "__main__":
    from kivy.lang import Builder  # to freely pick kivy files

    # Define different display settings based on an index.
    # 0: Full-screen on any display,
    # 1: Portrait,
    # 2: Elongated Portrait,
    # 3: Raspberry Pi touchscreen - Landscape,
    # 4: Raspberry Pi touchscreen - Portrait,
    # 5: Large square
    display_settings = {0: {'fullscreen': False, 'run': Window.maximize},  # Full-screen on any display
                        1: {'fullscreen': False, 'size': (600, 1000)},  # Portrait
                        2: {'fullscreen': False, 'size': (500, 1000)},  # Portrait elongated
                        3: {'fullscreen': False, 'size': (640, 480)},  # Raspi touchscreen - landscape
                        4: {'fullscreen': False, 'size': (480, 640)},  # Raspi touchscreen - portrait
                        5: {'fullscreen': False, 'size': (1200, 1200)}  # Large square
                        }

    dotenv.load_dotenv(DOTENV_PATH)
    style_code = int(os.getenv("SCREENMODE_BEVOR"))

    Window.fullscreen = display_settings[style_code]['fullscreen']
    if 'size' in display_settings[style_code].keys(): Window.size = display_settings[style_code]['size']
    if 'run' in display_settings[style_code].keys(): display_settings[style_code]['run']()

    # Load a specified Kivy file from the command-line argument or a default file.
    try:
        content = Builder.load_file(str(sys.argv[1]))
    except IndexError:
        content = Builder.load_file("kivy_sallet_BEVOR.kv")

    # Create an instance of the SalletBEVOR app with loaded content and a content size multiplier.
    application = SalletBEVOR(window_content=content, csm=1, dotenv_path=DOTENV_PATH)

    # Run the Kivy application with defined settings.
    application.run()
    
    # Close any existing OpenCV windows.
    cv2.destroyAllWindows()

    # tx_id = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # tx_id = "4bb697b2f8e6160c8ac91fcdfb9acafe3011d44e23f745c301e569a1b3b4a679"  # many outputs
    # tx_id = "d53cb2720b9b00d80aced71d2f68bce2301cab5d3e073fc86838bb62f1abdb4f"  # coinbase related
    # tx_id = "785822e4f31959ea9b0e3eca7ff9208dd45f968549baa45a66c1155efb28443f"  # tons of inputs - long calc!!!
    # tx_id = "44932e0abb2e8ee770cae42ec4f1a3dc68a4663bb8da87e56258a33b67f68f4a"  # many on both sides
    # tx_id = "21bb393e74b1828e627b985186ef9a93e39e81726613458c3a68bf956757d413"  # general tx
    # tx_id = "dfec52f1557a335185af663b02b84bf517a02dece9fc1f7dd3abfae03696c094"  # ideal for test
    # tx_id = "e44d6f3f6cd8b8beaefcc7449b88c4fe47ac67af5e899cb2c21d2de663914d69"  # ideal for test
    # tx_id = "12779f6f559eb8375c81f09ef5d358cc759432a3b789b82b2a2a5508de9100dd"  #
    # tx_id = "ffe43993741fa8cb6dbc94316a2f5011730e3a1bec269075a3ccbb82a098f4d0"
    # tx_id = "0570eb5d0f361a9f5664c20426d5633997f00aff45dcc50c4f49bec7f99eb7ee"
