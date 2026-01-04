# -----------------------------------------------
# 🔸 SanyaMusic Project
# 🔹 Developed & Maintained by: Stark (https://github.com/urstark)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by urstark
# -----------------------------------------------
from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SANYAMUSIC import app


def help_pannel(_, page_num: int = 1):
    all_buttons = [
        # Core Music
        InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11"), # Play
        InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1"),   # Admin
        InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6"),   # C-Play
        InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8"),   # Loop
        InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12"), # Shuffle
        InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13"), # Seek
        InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15"), # Speed
        # Info & Search
        InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14"), # Song/Search
        InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10"), # Ping
        InlineKeyboardButton(text=_["H_B_20"], callback_data="help_callback hb20"), # Info
        InlineKeyboardButton(text=_["H_B_24"], callback_data="help_callback hb24"), # Search
        # Sudo & Management
        InlineKeyboardButton(text=_["H_B_34"], callback_data="help_callback hb34"), # Sudo
        InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2"),   # Auth
        InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3"),   # G-Cast
        InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7"),   # G-Ban
        InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5"),   # BL-User
        InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4"),   # BL-Chat
        InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9"),   # Log
        InlineKeyboardButton(text=_["H_B_35"], callback_data="help_callback hb35"), # Clone
        # Fun & Extras
        InlineKeyboardButton(text=_["H_B_16"], callback_data="help_callback hb16"), # ChatGPT
        InlineKeyboardButton(text=_["H_B_17"], callback_data="help_callback hb17"), # Group
        InlineKeyboardButton(text=_["H_B_18"], callback_data="help_callback hb18"), # Stickers
        InlineKeyboardButton(text=_["H_B_19"], callback_data="help_callback hb19"), # Tag
        InlineKeyboardButton(text=_["H_B_21"], callback_data="help_callback hb21"), # Extra
        InlineKeyboardButton(text=_["H_B_22"], callback_data="help_callback hb22"), # Image
        InlineKeyboardButton(text=_["H_B_23"], callback_data="help_callback hb23"), # Action
        InlineKeyboardButton(text=_["H_B_25"], callback_data="help_callback hb25"), # Font
        InlineKeyboardButton(text=_["H_B_26"], callback_data="help_callback hb26"), # Games
        InlineKeyboardButton(text=_["H_B_27"], callback_data="help_callback hb27"), # T-Graph
        InlineKeyboardButton(text=_["H_B_28"], callback_data="help_callback hb28"), # Imposter
        InlineKeyboardButton(text=_["H_B_29"], callback_data="help_callback hb29"), # Truth-Dare
        InlineKeyboardButton(text=_["H_B_30"], callback_data="help_callback hb30"), # Hashtag
        InlineKeyboardButton(text=_["H_B_31"], callback_data="help_callback hb31"), # TTS
        InlineKeyboardButton(text=_["H_B_32"], callback_data="help_callback hb32"), # Fun
        InlineKeyboardButton(text=_["H_B_33"], callback_data="help_callback hb33"), # Quotly
    ]

    # 15 buttons per page, 5 rows of 3 buttons
    BUTTONS_PER_ROW = 3
    ROWS_PER_PAGE = 5

    # Create rows of 3 buttons
    button_rows = [all_buttons[i : i + BUTTONS_PER_ROW] for i in range(0, len(all_buttons), BUTTONS_PER_ROW)]

    # Create pages with 4 rows each
    pages = [button_rows[i : i + ROWS_PER_PAGE] for i in range(0, len(button_rows), ROWS_PER_PAGE)]
    total_pages = len(pages)

    try:
        page_buttons = pages[page_num - 1]
    except IndexError:
        return None

    nav_row = []
    # Previous button (loops to last page from first)
    prev_page = total_pages if page_num == 1 else page_num - 1
    nav_row.append(
        InlineKeyboardButton(
            text=_["BACK_PAGE"], callback_data=f"help_page {prev_page}"
        )
    )

    # Back to Start Menu button
    nav_row.append(
        InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_back_helper")
    )

    # Next button (loops to first page from last)
    next_page = 1 if page_num == total_pages else page_num + 1
    nav_row.append(
        InlineKeyboardButton(
            text=_["NEXT_PAGE"], callback_data=f"help_page {next_page}"
        )
    )

    page_buttons.append(nav_row)
    page_buttons.append([InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")])
    return InlineKeyboardMarkup(page_buttons)


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"open_help_panel",
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]
    return buttons
