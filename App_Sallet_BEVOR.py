"""Sallet univers' BEVOR app.
by Sziller"""

import os
import sys
import cv2
import dotenv
import inspect
import logging
from typing import Optional
from kivy.app import App  # necessary for the App class
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.uix.image import AsyncImage

from SalletBasePackage.WidgetClasses import *
from SalletBasePackage import SQL_interface as sql
from SalletBasePackage.decorators import *
from SalletBasePackage import DataDisplay as DaDi
from SalletNodePackage.NodeManager import NODEManager
from SalletNodePackage.BitcoinNodeObject import Node as btcNode
from sql_bases.sqlbase_node.sqlbase_node import Node as sqlNode
from kivy.config import Config
import config as conf

lg = logging.getLogger()
lg.info("START: {:>85} <<<".format('App_Sallet_BEVOR.py'))

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
SCREENNAMES = conf.SCREENNAMES


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
        self.statedict: Optional[dict] = None
        # ----------------------------------------------------------------------
        self.generate_statedict()

    def generate_statedict(self):
        """=== Instance method =========================================================================================
        Generates the statedict, from a list of screen-names
        ========================================================================================== by Sziller ==="""
        self.statedict = {}
        # Loop over each item in the list with its index
        for idx, item in enumerate(SCREENNAMES):
            screen_key = f"screen_{item}"
            inst_key = f"button_nav_{item}"
            # Construct the dictionary entry
            self.statedict[screen_key] = {
                "seq": idx,
                "inst": inst_key,
                "down": [inst_key],
                "normal": [f"button_nav_{other}" for other in SCREENNAMES if other != item]}


class OpAreaIntro(OperationAreaBox):
    ccn = inspect.currentframe().f_code.co_name
    
    def __init__(self, **kwargs):
        super(OpAreaIntro, self).__init__(**kwargs)

    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        print("Started: {}".format(self.ccn))


class OpAreaCommand(OperationAreaBox):
    """
    This class represents the operation area for the Command screen.
    It contains manually defined CommandRowObj instances and manages their activation and command execution.
    """
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self, **kwargs):
        super(OpAreaCommand, self).__init__(**kwargs)
        self.memorized_btn_color: tuple or None = None  # workaround to gain button color from .kv
        self.memorized_btn_text: str or None = None  # workaround to gain button text from .kv
        self.list_of_rows = [1, 2, 3, 4, 5, 6]
        
        self.tx_id: Optional[str]       = None
        self.blk_seqnr: Optional[int]   = None
        self.blk_hash: Optional[str]    = None
        
    def _reset_stored_data(self):
        """ Private instance method ====================================================================================
        Resets text entry defined parameters
        ========================================================================================== by Sziller ==="""
        self.tx_id: str = ''
        self.blk_seqnr: int = 0
        self.blk_hash: str = ""
        
    def on_init(self):
        """=== Method name: on_init ====================================================================================
        Default method to run right after startup (or whenever defaulting back to initial state is necessary)
        ========================================================================================== by Sziller ==="""
        for rownr in self.list_of_rows:
            self._deactivate_row(row_nr=rownr)
    
    def _row_activation_mngr(self, row_nr):
        """ Private instance method ====================================================================================
        Calling widget manipulation methods
        ========================================================================================== by Sziller ==="""
        self._activate_row(row_nr=row_nr)
        for rownr in self.list_of_rows:
            self._deactivate_row(row_nr=rownr) if rownr != row_nr else None

    def _activate_row(self, row_nr: int):
        """=== Instance method =========================================================================================
        Activates the specified row , while disabling its toggle button
        ========================================================================================== by Sziller ==="""
        self.ids['btn_cmd_act_{:>02}'.format(row_nr)].disabled = True
        self.ids['btn_cmd_issue_{:>02}'.format(row_nr)].disabled = False
        self.ids['inp_cmd_{:>02}'.format(row_nr)].disabled = False
        
    def _deactivate_row(self, row_nr: int):
        """=== Instance method =========================================================================================
        Deativates the specified row , while enabling its toggle button
        ========================================================================================== by Sziller ==="""
        self.ids['btn_cmd_act_{:>02}'.format(row_nr)].disabled = False
        self.ids['btn_cmd_issue_{:>02}'.format(row_nr)].disabled = True
        self.ids['inp_cmd_{:>02}'.format(row_nr)].disabled = True
        self.ids['inp_cmd_{:>02}'.format(row_nr)].text = ""
        self.ids.lbl_tx_info.text = ""

    def on_textupdate_txid(self, inst):
        self.tx_id = str(inst.text)
    
    def on_textupdate_seqnr(self, inst):
        try:
            self.blk_seqnr = int(inst.text)
        except ValueError:
            print ("SHIT")

    @log_button_click
    def on_release_getconnectioncount(self):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        data_as_displayed = "The Node's number of connection is: {}".format(
            App.get_running_app().actual_node_object.nodeop_getconnectioncount())
        self.ids.lbl_tx_info.text = data_as_displayed
        
    @log_button_click
    def on_release_getblockcount(self):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        data_as_displayed = "Current blockcount is: {}".format(
            App.get_running_app().actual_node_object.nodeop_getblockcount())
        self.ids.lbl_tx_info.text = data_as_displayed
    
    @log_button_click
    def on_release_getblockhash(self):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        data_as_displayed = "Block Nr. {}'s hash is:\n {}".format(self.blk_seqnr,
            App.get_running_app().actual_node_object.nodeop_getblockhash(sequence_nr=self.blk_seqnr))
        self.ids.lbl_tx_info.text = data_as_displayed

    @log_button_click
    def on_release_check_tx_confirmation(self):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        data_as_displayed = "Transaction is {}".format(
            {True: 'CONFIRMED', False: 'NOT CONFIRMED YET'}
            [App.get_running_app().actual_node_object.nodeop_check_tx_confirmation(tx_hash=self.tx_id)])
        self.ids.lbl_tx_info.text = data_as_displayed

    @log_button_click
    def on_release_count_tx_confirmation(self):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        data_as_displayed = "Transaction has confirmations: {}".format(
            App.get_running_app().actual_node_object.nodeop_confirmations(tx_hash=self.tx_id))
        self.ids.lbl_tx_info.text = data_as_displayed

    @log_button_click
    def on_buttonclick_showtx(self, inst):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        if self.memorized_btn_color is None:
            self.memorized_btn_color = inst.background_color
            self.memorized_btn_text = inst.text

        tx_id = self.tx_id
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

    @log_button_click
    @run_internal_reset
    def on_buttonclick_toggle(self, inst):
        """=== Instance method: buttonclick ============================================================================
        ========================================================================================== by Sziller ==="""
        self._row_activation_mngr(inst.cmdnr)


class SalletBEVOR(App):
    """=== Class name: SalletBEVOR =====================================================================================
    Child of built-in class: App
    This is the Parent application for the Sealed of Kex manager project.
    Instantiation should - contrary to what is used on the net - happen by assigning it to a variable name.
    :param window_content:
    ============================================================================================== by Sziller ==="""
    
    def __init__(self, window_content: str, window_title: str, csm: float = 1.0, dotenv_path="./.env"):
        super(SalletBEVOR, self).__init__()
        self.window_content                 = window_content
        self.content_size_multiplier: float = csm
        # ----------------------------------------------------------------------
        self.dotenv_path: str               = dotenv_path
        dotenv.load_dotenv(self.dotenv_path)
        self.title: str                     = window_title
        self.balance_onchain_sats: int      = 0
        # --- Database settings ---------------------------------------------   - Database settings -   START   -
        # TODO: check sql source!
        self.db_session = sql.createSession(db_path=os.getenv("DB_PATH_BEVOR"),
                                            style=os.getenv("DB_STYLE_BEVOR"))
        # --- Database settings ---------------------------------------------   - Database settings -   ENDED   -

        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   START   -
        self.unit_base: str         = os.getenv("UNIT_BASE")
        self.unit_use: str          = os.getenv("UNIT_USE")
        self.display_format: str    = os.getenv("DISPLAY_FORMAT") + " " + os.getenv("UNIT_USE")
        # --- Bitcoin related settings ----------------------------------  Bitcoin related settings -   ENDED   -
        # --- Node related settings -------------------------------------  Node related settings    -   START   -
        self.nodemanager: NODEManager = NODEManager(dotenv_path="./.env",
                                                    row_obj=sqlNode.__table__,
                                                    session_in=self.db_session)
        self.actual_node_object: Optional[btcNode] = None
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
        self.nodemanager.get_key_guided_rowdict()
        self.on_release_switch_node(target_alias=os.getenv("DEFAULT_NODE"))
        # --- Setting default Node                                                              ENDED   -
    
    def update_node_info(self):
        """Update both the Ribbon and the label with current node info."""
        # Update the Ribbon text on all screens
        alias = self.actual_node_object.alias
        is_rpc = self.actual_node_object.is_rpc
        
        print(self.root.ids.screen_intro.ids.ribbon_intro.text_ribbon)
        msg = "Node: {} - {}".format(alias, {True: "RPC", False: "API"}[is_rpc])
        self.root.ids.screen_intro.ids.ribbon_intro.text_ribbon = msg
        self.root.ids.screen_command.ids.ribbon_command.text_ribbon = msg

    def update_node_label(self):
        """Update the detailed node label on the Welcome screen."""
        node = self.actual_node_object
        label_text = f"{node.alias}\n"
        if node.is_rpc:
            label_text +=   f"RPC\n" \
                            f"{node.rpc_ip}:{node.rpc_port}\n"
        else:
            label_text +=   f"API\n" \
                            f"{node.ext_node_url}\n"
        label_text +=       f"{node.owner}\n" \
                            f"{node.features}\n" \
                            f"{node.desc}"
        self.root.ids.screen_intro.ids.oparea_intro.ids.lbl_node_selection.text = label_text

    @log_button_click
    def on_release_switch_node(self, target_alias: Optional[str] = None):
        """Method to switch the active node when the button is pressed."""
        self.actual_node_object = self.nodemanager.return_next_node_instance()
        if target_alias and target_alias.lower() in self.nodemanager.node_obj_dict:
            while target_alias.lower() != self.actual_node_object.alias:
                self.actual_node_object = self.nodemanager.return_next_node_instance()
        print("-------------------------------------------------")
        # Update Ribbon and label after switching the node
        self.update_node_info()
        # Update the node info label on the Welcome screen
        self.update_node_label()


if __name__ == "__main__":
    import sys
    import config as conf
    import argparse
    from kivy.lang import Builder  # to freely pick kivy files
    from kivy.core.window import Window
    
    DOTENV_PATH = "./.env"
    
    def parse_args():
        """=== Parser ===
        by Sziller ==="""
        parser = argparse.ArgumentParser(description="Run the Kivy application with options.")
        parser.add_argument("--kv-file", type=str, help="Path to the .kv file to load.")
        parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode.")
        parser.add_argument("--window-size", type=str, help="Window size in WIDTHxHEIGHT format.")
        return parser.parse_args()
    
    # Parse command-line arguments
    args = parse_args()

    display_settings    = conf.DISPLAY_SETTINGS
    style_code          = conf.SCREENMODE_BEVOR

    Window.fullscreen = display_settings[style_code]['fullscreen']
    if 'size' in display_settings[style_code].keys():
        Window.size = display_settings[style_code]['size']

    if args.window_size:
        try:
            width, height = map(int, args.window_size.split('x'))
            Window.size = (width, height)
        except ValueError:
            print("Invalid window size format. Use WIDTHxHEIGHT (e.g., 800x600).")

    if 'run' in display_settings[style_code].keys():
        display_settings[style_code]['run']()

    # Load a specified Kivy file from the command-line argument or a default file.
    try:
        content = Builder.load_file(args.kv_file) if args.kv_file else Builder.load_file(conf.KIVY_PATH)
    except Exception as e:
        print(f"Error loading .kv file: {e}")
        sys.exit(1)

    # Create an instance of the SalletBEVOR app with loaded content and a content size multiplier.
    application = SalletBEVOR(window_content=content,
                              window_title=conf.WINDOW_TITLE,
                              dotenv_path=DOTENV_PATH,
                              csm=1)

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
