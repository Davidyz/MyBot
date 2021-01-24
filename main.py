import telegram, logging, os, re, psutil, settings
import downloader, authentication, system, lang

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

downloads = []
AllowedUser = Filters.user(username=[i.replace('\n', '') for i in open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r').readlines()])
Admin = Filters.user(username='David_yz')
language = lang.en_UK

def start(update, context):
    '''
    Starting message.
    '''
    update.message.reply_text(language['welcome'])

def add_user(update, context):
    ''
    if authentication.validate(update.message.chat_id):
        # check for admin.
        AllowedUser.add_usernames([i.replace('@', '') for i in context.args])

        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            allowed = set(fin.readlines())
        allowed |= set(context.args)
        
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'w') as fin:
            for i in allowed:
                if i[-1] != '\n':
                    fin.write(i.replace('@', '') + '\n')
                else:
                    fin.write(i.replace('@', ''))
        update.message.reply_text('Added.')
    else:
        update.message.reply_text('You are unauthorized to perform this action.')

def remove_user(update, context):
    ''
    if authentication.validate(update.message.chat_id):
        # check for admin.
        AllowedUser.remove_usernames([i.replace('@', '') for i in context.args])
        
        allowed = []
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            allowed = [i.replace('\n', '') for i in fin.readlines()]
        
        for i in context.args:
            if i.replace('\n', '').replace('@', '') in allowed:
                allowed.remove(i.replace('\n', '').replace('@', ''))
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'w') as fin:
            for i in allowed:
                fin.write(i + '\n')
        update.message.reply_text('Removed.')
    else:
        update.message.reply_text('You are unauthorized to perform this action.')

def set_lang(update, context):
    global language
    language_list = {
            'chinese':lang.zh_CN,
            'english':lang.en_UK,
            }
    if len(context.args) == 1 and context.args[0].lower() in language_list:
        language = language_list[context.args[0].lower()]
        update.message.reply_text(language['lang_updated'])

    else:
        update.message.reply_text(language['check_input'])

def list_user(update, context):
    if authentication.validate(update.message.chat_id):
        # check for admin.
        with open(os.sep.join([settings.CWD, 'allowed_user.txt']), 'r') as fin:
            users = tuple(i.replace('\n', '') for i in fin.readlines())

        update.message.reply_text('Allowed users:\n' + '\n'.join(['@' + i for i in users]))
    else:
        update.message.reply_text('You are not authorized to perform this action.')

def help_command(update, context):
    '''
    Help message.
    '''
    message = 'Current function:\n - Download videos from Youtube at max quality by sending the url of the video;\n - /list_downloading list all videos being downloaded.'
    update.message.reply_text(language['help'])

def Action(update, context):
    '''
    Reply the same text as the user sent.
    '''
    global downloads
    message = update.message.text
    video_check = downloader.check_type(message)
    if video_check:
        update.message.reply_text(language['trying'].format(video_check[0].upper() + video_check[1:].lower()))
        dl = downloader.Downloader(update=update, context=context)
        if dl.download(message, site=video_check):
            downloads.append(dl)
        else:
            update.message.reply_text('This video source is not supported yet.')

    else:
        update.message.reply_text(update.message.text)

def isVideoUrl(url):
    WebPattern = "https://(www\.)*youtu(\.)*be(\.com)*.*"
    return re.match(WebPattern, url) != None

def checkFinished(context):
    global downloads
    finished = []
    empty_job = []
    for i in downloads:
        result = i.check_finished()
        if result:
            finished.append(i)

    for job in finished:
        finished_downloads = job.finished
        for i in finished_downloads:
            job.update.message.reply_text(text=language['finished_download'].format(finished_downloads[i]))
        if job.all_finished():
            empty_job.append(job)

    while empty_job:
        job = empty_job.pop(0)
        downloads.remove(job)
        del job

def get_downloading(update, context):
    '''
    To display the videos being downloaded.
    '''
    global downloads
    result = []
    for i in downloads:
        i.check_finished()
        if i.context[0].chat_data == context.chat_data:
            result += i.get_downloading()
    if result:
        update.message.reply_text('\n'.join([language['current_job']] + result))
    else:
        update.message.reply_text(language['no_job'])
    return result

def sys_info(update, context):
    '''
    To display the system information.
    '''
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    temperature = round(sum([psutil.sensors_temperatures()['coretemp'][i][1] for i in range(psutil.cpu_count())]) / psutil.cpu_count(), 2)
    update.message.reply_text('CPU utilization: {}%\nMemory utilization: {}%\nTemperature: {}°C'.format(cpu, mem, temperature))

def admin_help(update, context):
    update.message.reply_text('/list_user\n/sys_info')

def main():
    updater = Updater(settings.SECRETS, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command, filters=AllowedUser))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & AllowedUser, Action))
    dispatcher.add_handler(CommandHandler('list_downloading', get_downloading, filters=AllowedUser))
    dispatcher.add_handler(CommandHandler("sys_info", sys_info, filters=Admin))
    dispatcher.add_handler(CommandHandler('add_user', add_user))
    dispatcher.add_handler(CommandHandler('remove_user', remove_user))
    dispatcher.add_handler(CommandHandler('list_user', list_user))
    dispatcher.add_handler(CommandHandler('admin_help', admin_help, filters=Admin))
    dispatcher.add_handler(CommandHandler('set_lang', set_lang, filters=AllowedUser))

    dispatcher.job_queue.run_repeating(checkFinished, interval=10)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
