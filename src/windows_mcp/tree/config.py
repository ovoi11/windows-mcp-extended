INTERACTIVE_CONTROL_TYPE_NAMES = set(
    [
        "ButtonControl",
        "ListItemControl",
        "MenuItemControl",
        "EditControl",
        "CheckBoxControl",
        "RadioButtonControl",
        "ComboBoxControl",
        "HyperlinkControl",
        "SplitButtonControl",
        "TabItemControl",
        "TreeItemControl",
        "DataItemControl",
        "HeaderItemControl",
        "TextBoxControl",
        "SpinnerControl",
        "SliderControl",
        "ScrollBarControl",
    ]
)

INTERACTIVE_ROLES = {
    "PushButton",
    "SplitButton",
    "ButtonDropDown",
    "ButtonMenu",
    "ButtonDropDownGrid",
    "OutlineButton",
    "Link",
    "Text",
    "IpAddress",
    "HotkeyField",
    "ComboBox",
    "DropList",
    "CheckButton",
    "RadioButton",
    "MenuItem",
    "ListItem",
    "PageTab",
    "OutlineItem",
    "Slider",
    "SpinButton",
    "Dial",
    "ScrollBar",
    "Grip",
    "ColumnHeader",
    "RowHeader",
    "Cell",
}

DOCUMENT_CONTROL_TYPE_NAMES = set(["DocumentControl"])

STRUCTURAL_CONTROL_TYPE_NAMES = set([
    "PaneControl",
    "GroupControl",
    "CustomControl",
    "ToolBarControl",
    "TabControl",
    "MenuBarControl",
])

INFORMATIVE_CONTROL_TYPE_NAMES = set(
    [
        "TextControl",
        "ImageControl",
        "StatusBarControl",
    ]
)

DEFAULT_ACTIONS = set(["Click", "Press", "Jump", "Check", "Uncheck", "Double Click"])

THREAD_MAX_RETRIES = 3
