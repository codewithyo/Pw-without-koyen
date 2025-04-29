def create_html_file(file_name, batch_name, contents):
    # Use downloads directory for HTML files too
    file_name = os.path.join(DOWNLOADS_DIR, os.path.basename(file_name))
    content_cards = ''
    batch_thumbnail = ''
    
    # Find first image URL for thumbnail
    for line in contents:
        if ':' in line:
            text, url = [item.strip('\n').strip() for item in line.split(':', 1)]
            if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                batch_thumbnail = url
                break
    
    # Process content, skipping image URLs
    for line in contents:
        if ':' in line:
            text, url = [item.strip('\n').strip() for item in line.split(':', 1)]
            # Skip image URLs
            if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                continue
            
            if url.lower().endswith('.pdf'):
                content_cards += f'<div class="content-card"><a href="javascript:void(0)" onclick="openPdf(\'{url}\')">{text}</a></div>\n'
            elif url.endswith(('.m3u8', '.mp4')):
                content_cards += f'<div class="content-card"><a href="javascript:void(0)" onclick="playVideo(\'{url}\')">{text}</a></div>\n'
            else:
                content_cards += f'<div class="content-card"><a href="{url}" target="_blank">{text}</a></div>\n'

    with open('template.html', 'r', encoding='utf-8') as fp:
        file_content = fp.read()

    # Replace content and batch info
    file_content = file_content.replace('tbody_content', content_cards)
    file_content = file_content.replace('batch_name', batch_name)
    file_content = file_content.replace('BATCH_THUMBNAIL', batch_thumbnail if batch_thumbnail else 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'80\' height=\'80\' viewBox=\'0 0 24 24\'%3E%3Cpath fill=\'%23e5e7eb\' d=\'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4z\'/%3E%3C/svg%3E')

    with open(file_name, 'w', encoding='utf-8') as fp:
        fp.write(file_content)





async def handle_main_callbacks(bot: Client, callback_query):
    """Handle main feature callbacks"""
    try:
        if not callback_query.from_user:
            logger.error("Missing user information in callback query")
            await callback_query.answer("Error: Please try again", show_alert=True)
            return

        user_id = callback_query.from_user.id
        callback_data = callback_query.data

        # Process the callback without channel restriction
        if callback_data == "cpwp":
            await callback_query.answer()
            THREADPOOL.submit(asyncio.run, process_cpwp(bot, callback_query.message, user_id))
        elif callback_data == "txt2html":
            await txt2html_callback(bot, callback_query)
            
    except Exception as e:
        logger.error(f"Error in main callback handler: {str(e)}")
        await callback_query.answer("An error occurred. Please try again.", show_alert=True)


@bot.on_callback_query(filters.regex("^txt2html$"))
async def txt2html_callback(bot, callback_query):
    async with user_semaphore:  # Limit concurrent users
        user_id = callback_query.from_user.id
        
        if not await check_user_in_channel(bot, user_id):
            await callback_query.answer("Please join our channel first!", show_alert=True)
            return
            
        await callback_query.answer()
        msg = await callback_query.message.reply_text(
            "**Please send me the TXT file you want to convert to HTML.\n"
            "You are in queue. Maximum 15 users can be processed simultaneously.**"
        )
        
        try:
            cleanup_old_files()  # Cleanup old files before processing
            
            file_msg = await bot.listen(chat_id=callback_query.message.chat.id, filters=filters.document, timeout=300)
            
            if not file_msg.document.file_name.endswith('.txt'):
                await msg.edit("**Please send a TXT file only!**")
                return
                
            await msg.edit("**Processing...**")
            
            # Download to the downloads directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(DOWNLOADS_DIR, f"{user_id}_{timestamp}_input.txt")
            
            await file_msg.download(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents = f.readlines()
                
                if not contents:
                    await msg.edit("**The file is empty!**")
                    return
                    
                batch_name = os.path.splitext(file_msg.document.file_name)[0]
                html_file = os.path.join(DOWNLOADS_DIR, f"{user_id}_{batch_name}_{timestamp}.html")
                
                create_html_file(html_file, batch_name, contents)
                
                await msg.delete()
                await bot.send_document(
                    callback_query.message.chat.id,
                    document=html_file,
                    caption=f"**Here's your HTML file with embedded player!\nTotal entries: {len(contents)}**",
                    file_name=f"{batch_name}.html"
                )
                
            except Exception as e:
                await msg.edit(f"**Error processing file: {str(e)}**")
            finally:
                # Cleanup input files immediately after processing
                try:
                    os.remove(file_path)
                    os.remove(html_file)
                except:
                    pass
                    
        except ListenerTimeout:
            await msg.edit("**Timeout! Please try again.**")
        except Exception as e:
            await msg.edit(f"**Error: {str(e)}**")

