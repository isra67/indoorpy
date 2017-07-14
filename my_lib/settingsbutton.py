#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.uix.button import Button
from kivy.uix.settings import SettingItem
"""
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingOptions, SettingSpacer
from kivy.uix.widget import Widget
"""


# ###############################################################
#
# Declarations
#
# ###############################################################

class SettingButtons(SettingItem):

    def __init__(self, **kwargs):
        self.register_event_type('on_release')

        super(SettingItem, self).__init__(**kwargs)

        for aButton in kwargs["buttons"]:
            oButton = Button(text=aButton['title'], font_size='15sp')
            oButton.ID = aButton['id']
            self.add_widget(oButton)
            oButton.bind(on_release=self.On_ButtonPressed)


    def set_value(self, section, key, value):
        # set_value normally reads the configparser values and runs on an error
	# to do nothing here
        return


    def On_ButtonPressed(self,instance):
        self.panel.settings.dispatch('on_config_change',self.panel.config, self.section, self.key, instance.ID)


# ###############################################################
"""
class SettingScrollOptions(SettingOptions):

    def _create_popup(self, instance):
        "create the popup"

        content         = GridLayout(cols=1, spacing='5dp')
        scrollview      = ScrollView( do_scroll_x=False)
        scrollcontent   = GridLayout(cols=1,  spacing='5dp', size_hint=(None, None))
        scrollcontent.bind(minimum_height=scrollcontent.setter('height'))
        self.popup   = popup = Popup(content=content, title=self.title, size_hint=(0.5, 0.9),  auto_dismiss=False)

        # we need to open the popup first to get the metrics
        popup.open()

        # Add some space on top
        content.add_widget(Widget(size_hint_y=None, height=2))

        # add all the options
        uid = str(self.uid)
        for option in self.options:
            state = 'down' if option == self.value else 'normal'
            btn = ToggleButton(text=option, state=state, group=uid, size=(popup.width, 55), size_hint=(None, None))
            btn.bind(on_release=self._set_option)
            scrollcontent.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        scrollview.add_widget(scrollcontent)
        content.add_widget(scrollview)
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size=(popup.width, 50),size_hint=(0.9, None))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
"""

