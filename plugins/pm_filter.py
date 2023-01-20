# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from plugins.admin_check import admin_fliter
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pv_filter(client, message):
    kd = await global_filters(client, message)
    if kd == False:
        await auto_filter(client, message)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    await global_filters(client, message)
    mf = await manual_filters(client, message)
    if mf == False:
        await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("𝖳𝗁𝗂𝗌 𝗂𝗌 𝗇𝗈𝗍 𝖿𝗈𝗋 𝗒𝗈𝗎...", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("𝖸𝗈𝗎 𝖺𝗋𝖾 𝗎𝗌𝗂𝗇𝗀 𝗈𝗇𝖾 𝗈𝖿 𝗆𝗒 𝗈𝗅𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌, 𝗉𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝖺𝗀𝖺𝗂𝗇.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🔖{get_size(file.file_size)}🔰{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton(f'🔮 {search} 🔮', 'reqst')
        ]
    )
    btn.insert(1,
        [
            InlineKeyboardButton(f'📝 𝖳𝗂𝗉𝗌', 'info'),
            InlineKeyboardButton("🔎 𝖦𝗈𝗈𝗀𝗅𝖾", url=f"https://www.google.com/search?q={search}")
        ]
    )

    if 0 < offset <= 5:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 5
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("◀️ 𝖡𝖠𝖢𝖪", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝖭𝖤𝖷𝖳 ▶️", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("◀️ 𝖡𝖠𝖢𝖪", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝖭𝖤𝖷𝖳 ▶️", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("𝖳𝗁𝗂𝗌 𝗂𝗌 𝗇𝗈𝗍 𝖿𝗈𝗋 𝗒𝗈𝗎...", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("𝖸𝗈𝗎 𝖺𝗋𝖾 𝖼𝗅𝗂𝖼𝗄𝗂𝗇𝗀 𝗈𝗇 𝖺𝗇 𝗈𝗅𝖽 𝖻𝗎𝗍𝗍𝗈𝗇 𝗐𝗁𝗂𝖼𝗁 𝗂𝗌 𝖾𝗑𝗉𝗂𝗋𝖾𝖽.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('𝖢𝗁𝖾𝖼𝗄𝗂𝗇𝗀 𝖿𝗈𝗋 𝖬𝗈𝗏𝗂𝖾 𝗂𝗇 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit('❕ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗠𝗼𝘃𝗶𝗲 𝗼𝗿 𝗦𝗲𝗿𝗶𝗲𝘀 𝗡𝗼𝘁 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 ❕\n\n❌𝖮𝖳𝖳 𝗈𝗋 𝖣𝖵𝖣 𝖭𝗈𝗍 𝖱𝖾𝗅𝖾𝖺𝗌𝖾𝖽❌\n‼️𝖳𝗒𝗉𝖾 𝖭𝖺𝗆𝖾 𝖶𝗂𝗍𝗁 𝖸𝖾𝖺𝗋‼️\n\n🔎𝖬𝗈𝗏𝗂𝖾 𝖨𝗌 𝖭𝗈𝗍 𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝗂𝗇 𝗍𝗁𝖾 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖱𝖾𝗉𝗈𝗋𝗍 𝗍𝗈 𝖠𝖽𝗆𝗂𝗇🔎\n\n📥 𝗥𝗲𝗽𝗼𝗿𝘁 𝘁𝗼 𝗔𝗱𝗺𝗶𝗻 𝗕𝘆 📥\n@raixpiro_bot')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Done !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Process Cancelled !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('<b><i>No such file exist.</b></i>')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        buttons = InlineKeyboardMarkup( [ [ InlineKeyboardButton('⚔️ 𝖯𝖨𝖱𝖮 𝖴𝖯𝖣𝖠𝖳𝖤𝖲 ⚔️', url='https://t.me/rai_info17') ] ] )

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=InlineKeyboardMarkup( [ [ InlineKeyboardButton('⚔️ 𝖯𝖨𝖱𝖮 𝖴𝖯𝖣𝖠𝖳𝖤𝖲 ⚔️', url='https://t.me/rai_info17') ] ] ),
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('𝖢𝗁𝖾𝖼𝗄 𝖯𝖬, 𝖨 𝗁𝖺𝗏𝖾 𝗌𝖾𝗇𝗍 𝖿𝗂𝗅𝖾𝗌 𝗂𝗇 𝖯𝖬', show_alert=True)
        except UserIsBlocked:
            await query.answer('𝖴𝗇𝖻𝗅𝗈𝖼𝗄 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗆𝖺𝗇𝗁 !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("𝖨 𝖫𝗂𝗄𝖾 𝖸𝗈𝗎𝗋 𝖲𝗆𝖺𝗋𝗍𝗇𝖾𝗌𝗌, 𝖡𝗎𝗍 𝖣𝗈𝗇'𝗍 𝖡𝖾 𝖮𝗏𝖾𝗋𝗌𝗆𝖺𝗋𝗍 😒 \n𝖩𝗈𝗂𝗇 𝖴𝗉𝖽𝖺𝗍𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖿𝗂𝗋𝗌𝗍 ;)", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        buttons = InlineKeyboardMarkup( [ [ InlineKeyboardButton('⚔️ 𝖯𝖨𝖱𝖮 𝖴𝖯𝖣𝖠𝖳𝖤𝖲 ⚔️', url='https://t.me/rai_info17') ] ] )
        
        
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            reply_markup=InlineKeyboardMarkup( [ [ InlineKeyboardButton('⚔️ 𝖯𝖨𝖱𝖮 𝖴𝖯𝖣𝖠𝖳𝖤𝖲 ⚔️', url='https://t.me/rai_info17') ] ] ),
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🔍 𝖲𝖾𝖺𝗋𝖼𝗁', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋', url='https://t.me/rai_info17')
        ], [
            InlineKeyboardButton('ℹ️ 𝖧𝖾𝗅𝗉', callback_data='help'),
            InlineKeyboardButton('😊 𝖠𝖻𝗈𝗎𝗍', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('⚔️ Manual Filter', callback_data='manuelfilter'),
            InlineKeyboardButton('🖥 Auto Filter', callback_data='autofilter')
        ], [
            InlineKeyboardButton('📡 Connection', callback_data='coct'),
            InlineKeyboardButton('💡 Extra Mods', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 𝖧𝗈𝗆𝖾', callback_data='start'),
            InlineKeyboardButton('♻️ 𝖲𝗍𝖺𝗍𝗎𝗌', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🤖 𝖴𝗉𝖽𝖺𝗍𝖾𝗌', url='https://t.me/rai_info17'),
            InlineKeyboardButton('♥️ 𝖲𝗈𝗎𝗋𝖼𝖾', callback_data='source')
        ], [
            InlineKeyboardButton('🏠 𝖧𝗈𝗆𝖾', callback_data='start'),
            InlineKeyboardButton('🔐 𝖢𝗅𝗈𝗌𝖾', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help'),
            InlineKeyboardButton('⏹️ 𝖡𝗎𝗍𝗍𝗈𝗇𝗌', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help'),
            InlineKeyboardButton('👮‍♂️ 𝖠𝖽𝗆𝗂𝗇', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help'),
            InlineKeyboardButton('♻️ 𝖱𝖾𝖿𝗋𝖾𝗌𝗁', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase...")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 𝖡𝖺𝖼𝗄', callback_data='help'),
            InlineKeyboardButton('♻️ 𝖱𝖾𝖿𝗋𝖾𝗌𝗁', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    elif query.data == 'reqst':
        await query.answer("𝖧𝖾𝗒 𝖡𝗋𝗈 😍\n\n🎯 𝖢𝗅𝗂𝖼𝗄 𝖮𝗇 𝖳𝗁𝖾 𝖡𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝖳𝗁𝖾 𝖥𝗂𝗅𝖾𝗌 𝖸𝗈𝗎 𝖶𝖺𝗇𝗍 𝖠𝗇𝖽 𝖲𝗍𝖺𝗋𝗍 𝖳𝗁𝖾 𝖡𝗈𝗍 ⬇️", True)
    elif query.data == 'info':
        await query.answer("𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝘀 𝗙𝗼𝗿𝗺𝗮𝘁𝘀\n\n• 𝖲𝗈𝗅𝗈 2017\n• 𝖣𝗁𝗈𝗈𝗆 3 𝖧𝗂𝗇𝖽𝗂\n• 𝖪𝗎𝗋𝗎𝗉 𝖪𝖺𝗇𝗇𝖺𝖽𝖺\n• 𝖣𝖺𝗋𝗄 𝗌01\n• 𝖲𝗁𝖾 𝖧𝗎𝗅𝗄 720𝗉\n• 𝖥𝗋𝗂𝖾𝗇𝖽𝗌 𝗌03 1080𝗉\n\n‼️𝗗𝗼𝗻𝘁 𝗮𝗱𝗱 𝘄𝗼𝗿𝗱𝘀 & 𝘀𝘆𝗺𝗯𝗼𝗹𝘀  , . - 𝗹𝗶𝗸𝗲 send link movie series 𝗲𝘁𝗰‼️", True)
    try: await query.answer('Piracy is Crime')
    except: pass


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id ,search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"🔖{get_size(file.file_size)}🔰{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton(f'🔮 {search} 🔮', 'reqst')
        ]
    )
    btn.insert(1,
        [
            InlineKeyboardButton(f'📝 𝖳𝗂𝗉𝗌', 'info'),
            InlineKeyboardButton("🔎 𝖦𝗈𝗈𝗀𝗅𝖾", url=f"https://www.google.com/search?q={search}")
        ]
    )    

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝖭𝖤𝖷𝖳 ▶️", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="📃 1/1", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>👋 𝖧𝖾𝗅𝗅𝗈 𝖳𝗁𝖾𝗋𝖾...!!!\n📁 𝖸𝗈𝗎𝗋 𝖥𝗂𝗅𝖾𝗌 𝖠𝗋𝖾 𝖱𝖾𝖺𝖽𝗒\n\n♨️ 𝖯𝗈𝗐𝖾𝗋𝖾𝖽 𝖡𝗒 @rai_info17</b>"
    if imdb and imdb.get('poster'):
        try:
            hehe =  await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(300)
                await hehe.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(300)
                await hmm.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            if SELF_DELETE:
                await asyncio.sleep(300)
                await fek.delete()
    else:
        fuk = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(300)
        await fuk.delete()        
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("<b><i>𝖨 𝖼𝗈𝗎𝗅𝖽𝗇'𝗍 𝖿𝗂𝗇𝖽 𝖺𝗇𝗒𝗍𝗁𝗂𝗇𝗀 𝗋𝖾𝗅𝖺𝗍𝖾𝖽 𝗍𝗈 𝗍𝗁𝖺𝗍. 𝗖𝗵𝗲𝗰𝗸 𝘆𝗼𝘂𝗿 𝘀𝗽𝗲𝗹𝗹𝗶𝗻𝗴</b></i>")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("<b><i>𝖨 𝖼𝗈𝗎𝗅𝖽𝗇'𝗍 𝖿𝗂𝗇𝖽 𝖺𝗇𝗒𝗍𝗁𝗂𝗇𝗀 𝗋𝖾𝗅𝖺𝗍𝖾𝖽 𝗍𝗈 𝗍𝗁𝖺𝗍. 𝗖𝗵𝗲𝗰𝗸 𝘆𝗼𝘂𝗿 𝘀𝗽𝗲𝗹𝗹𝗶𝗻𝗴</b></i>")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    load = btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    zz = await msg.reply('<b><i>𝖲𝖾𝖺𝗋𝖼𝗁𝗂𝗇𝗀 𝖿𝗈𝗋 𝗒𝗈𝗎 𝗋𝖾𝗌𝗎𝗅𝗍 𝗂𝗇 𝖨𝖬𝖣𝖻 \n𝖶𝖺𝗂𝗍....🧐<i/></b>')
    await asyncio.sleep(2)
    await zz.delete()
    sp = await msg.reply("<b>𝖨 𝖼𝗈𝗎𝗅𝖽𝗇'𝗍 𝖿𝗂𝗇𝖽 𝖺𝗇𝗒𝗍𝗁𝗂𝗇𝗀 𝗋𝖾𝗅𝖺𝗍𝖾𝖽 𝗍𝗈 𝗍𝗁𝖺𝗍\n𝖣𝗂𝖽 𝗒𝗈𝗎 𝗆𝖾𝖺𝗇 𝖺𝗇𝗒 𝗈𝗇𝖾 𝗈𝖿 𝗍𝗁𝖾𝗌𝖾?</b>",
                    reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(21)
    await sp.delete()


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            knd3 = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(300)
                            await knd3.delete()
                            await message.delete()

                        else:
                            button = eval(btn)
                            knd2 = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(300)
                            await knd2.delete()
                            await message.delete()

                    elif btn == "[]":
                        knd1 = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(300)
                        await knd1.delete()
                        await message.delete()

                    else:
                        button = eval(btn)
                        knd5 = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(300)
                        await knd5.delete()
                        await message.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            knd3 = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(300)
                            await knd3.delete()
                            await message.delete()

                        else:
                            button = eval(btn)
                            knd2 = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(300)
                            await knd2.delete()
                            await message.delete()

                    elif btn == "[]":
                        knd1 = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(300)
                        await knd1.delete()
                        await message.delete()

                    else:
                        button = eval(btn)
                        knd4 = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(300)
                        await knd4.delete()
                        await message.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
