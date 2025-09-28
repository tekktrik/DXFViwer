"""View DXF files if provided as an attachment to a part"""

from part.models import Part
from common.models import InvenTreeSetting
from django.db.models import Q

from django.core.exceptions import ValidationError

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UserInterfaceMixin

from . import PLUGIN_VERSION


def is_hex_color(color: str):
    """Determines whether the input is a valid hex color code."""

    error_text = "Must be a hex code of form '#44db44'"

    if len(color) != 7 or not color.startswith("#"):
        raise ValidationError(error_text)

    for char in color[1:]:
        char_ord = ord(char.lower())
        if not (48 <= char_ord <= 57 or 97 <= char_ord <= 102):
            raise ValidationError(error_text)

    return True


class DXFViewer(SettingsMixin, UserInterfaceMixin, InvenTreePlugin):
    """DXFViewer - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "DXF Viewer"
    NAME = "DXFViewer"
    SLUG = "dxf-viewer"
    DESCRIPTION = "View DXF files if provided as an attachment to a part"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Alec Delaney"
    WEBSITE = "https://github.com/tekktrik/inventree-dxf-viewer-plugin"
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    # Render custom UI elements to the plugin settings page
    ADMIN_SOURCE = "Settings.js:renderPluginSettings"

    # User interface elements (from UserInterfaceMixin)
    # Ref: https://docs.inventree.org/en/latest/plugins/mixins/ui/

    # Custom UI panels
    def get_ui_panels(self, request, context: dict, **kwargs):
        """Return a list of custom panels to be rendered in the InvenTree user interface."""

        # Only display this panel for the 'part' target
        if context.get("target_model") != "part":
            return []

        base_url = InvenTreeSetting.get_setting("INVENTREE_BASE_URL")

        primary_key = context.get("target_id")
        part = Part.objects.get(pk=primary_key)

        attachments = part.attachments.filter(Q(attachment__endswith=".dxf"))

        if not attachments:
            return []

        attachement_urls = [
            f"{base_url}/media/{attachment.attachment.name}"
            for attachment in attachments
        ]

        panels = []

        panels.append({
            "key": "dxf-viewer-panel",
            "title": "DXF Viewer",
            "description": "Custom panel description",
            "icon": "ti:file-3d:outline",
            "source": self.plugin_static_file("Panel.js:renderDXFViewerPanel"),
            "context": {
                # Provide additional context data to the panel
                "attachments": attachement_urls,
                "model_color": self.get_user_setting("MODEL_COLOR", request.user),
            },
        })

        return panels
